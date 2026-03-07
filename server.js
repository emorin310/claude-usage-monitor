require('dotenv').config();
const express = require('express');
const { WebSocketServer } = require('ws');
const chokidar = require('chokidar');
const fs = require('fs');
const path = require('path');
const http = require('http');

// ─── Config ──────────────────────────────────────────────────────────────────

const CLAUDE_DIR = path.join(process.env.HOME, '.claude');
const PROJECTS_DIR = path.join(CLAUDE_DIR, 'projects');
const STATS_CACHE = path.join(CLAUDE_DIR, 'stats-cache.json');
const SWIFT_SCRIPT = path.join(CLAUDE_DIR, 'fetch-claude-usage.swift');

const PORT = parseInt(process.env.PORT || '3847', 10);
const USAGE_POLL_MS = parseInt(process.env.USAGE_POLL_MS || '30000', 10);
const RATE_WINDOW_MS = 60_000; // 1-minute sliding window for token rate

// Read org ID and session key from env or fall back to the swift script
function readSwiftInjected(key) {
  try {
    const src = fs.readFileSync(SWIFT_SCRIPT, 'utf8');
    const match = src.match(new RegExp(`let injectedKey = "([^"]+)"`) );
    if (key === 'sessionKey' && match) return match[1].trim() || null;
    const orgMatch = src.match(/let injectedOrgId = "([^"]+)"/);
    if (key === 'orgId' && orgMatch) return orgMatch[1].trim() || null;
  } catch { /* ignore */ }
  return null;
}

let SESSION_KEY = process.env.CLAUDE_SESSION_KEY || readSwiftInjected('sessionKey');
let ORG_ID      = process.env.CLAUDE_ORG_ID      || readSwiftInjected('orgId');

// Update or add keys in .env without clobbering other entries
function writeEnv(updates) {
  const envPath = path.join(__dirname, '.env');
  let lines = [];
  try { lines = fs.readFileSync(envPath, 'utf8').split('\n'); } catch { /* new file */ }
  for (const [key, value] of Object.entries(updates)) {
    const idx = lines.findIndex(l => l.startsWith(key + '='));
    const line = `${key}=${value}`;
    if (idx >= 0) lines[idx] = line;
    else lines.push(line);
  }
  fs.writeFileSync(envPath, lines.filter((l, i) => l || i < lines.length - 1).join('\n') + '\n');
}

// ─── State ───────────────────────────────────────────────────────────────────

// sessionId -> { id, shortId, projectPath, projectLabel, firstPrompt,
//                model, modelHistory: Set, isSidechain,
//                tokens: { input, output, cacheRead, cacheCreate },
//                events: [{ ts, input, output, cacheRead, cacheCreate }],
//                lastSeen }
const sessions = new Map();

// filePath -> bytes already read
const fileOffsets = new Map();

// Rolling token events for rate calculation: [{ ts, total }]
const globalEvents = [];

// Daily token accumulator for weekly gauge: 'YYYY-MM-DD' -> total
const dailyTokens = new Map();

// Utilization from claude.ai API
let utilizationData = {
  fiveHour: { utilization: null, resetsAt: null },
  weekly:   { utilization: null, resetsAt: null },
  models:   {},   // modelName -> { weekly: { utilization, resetsAt } }
  fetchedAt: null,
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

function shortId(id) {
  return id.slice(0, 8);
}

function projectLabel(filePath) {
  const parts = filePath.split(path.sep);
  const projectIdx = parts.findIndex(p => p === 'projects');
  if (projectIdx === -1) return 'unknown';
  const encoded = parts[projectIdx + 1] || 'unknown';
  // Convert -Users-eric-Documents-Foo to ~/Documents/Foo
  return encoded
    .replace(/^-Users-[^-]+/, '~')
    .replace(/-/g, '/');
}

function tokensTotal(t) {
  return (t.input || 0) + (t.output || 0) + (t.cacheRead || 0) + (t.cacheCreate || 0);
}

// Tokens consumed in the last windowMs across all sessions
function computeRate(windowMs = RATE_WINDOW_MS) {
  const cutoff = Date.now() - windowMs;
  const recent = globalEvents.filter(e => e.ts >= cutoff);
  const total = recent.reduce((s, e) => s + e.total, 0);
  return { tokensPerMin: Math.round(total * (60_000 / windowMs)), windowTotal: total };
}

// Compute this-week vs last-week token totals (Mon–Sun weeks)
function computeWeekly() {
  const now = new Date();
  const dow = (now.getDay() + 6) % 7; // 0=Mon … 6=Sun
  const thisMonday = new Date(now);
  thisMonday.setHours(0, 0, 0, 0);
  thisMonday.setDate(now.getDate() - dow);
  const lastMonday = new Date(thisMonday);
  lastMonday.setDate(thisMonday.getDate() - 7);

  let thisWeek = 0, lastWeek = 0;
  for (const [dateKey, total] of dailyTokens) {
    const d = new Date(dateKey + 'T00:00:00');
    if (d >= thisMonday)   thisWeek += total;
    else if (d >= lastMonday) lastWeek += total;
  }
  return { thisWeek, lastWeek };
}

// Prune old global events beyond 10-minute window
function pruneGlobalEvents() {
  const cutoff = Date.now() - 10 * 60_000;
  let i = 0;
  while (i < globalEvents.length && globalEvents[i].ts < cutoff) i++;
  if (i > 0) globalEvents.splice(0, i);
}

// ─── JSONL Parsing ───────────────────────────────────────────────────────────

function processNewLines(filePath, newContent) {
  const lines = newContent.split('\n').filter(Boolean);

  for (const line of lines) {
    let obj;
    try { obj = JSON.parse(line); } catch { continue; }

    if (obj.type !== 'assistant') continue;
    const msg = obj.message;
    if (!msg || !msg.usage) continue;

    const usage = msg.usage;
    const inputTok  = usage.input_tokens || 0;
    const outputTok = usage.output_tokens || 0;
    const cacheRead = usage.cache_read_input_tokens || 0;
    const cacheCreate = usage.cache_creation_input_tokens || 0;
    const totalTok  = inputTok + outputTok + cacheRead + cacheCreate;

    if (totalTok === 0) continue;

    const sessionId = obj.sessionId || 'unknown';
    const model = msg.model || 'unknown';
    const ts = obj.timestamp ? new Date(obj.timestamp).getTime() : Date.now();
    const isSidechain = !!obj.isSidechain;

    // Update or create session record
    if (!sessions.has(sessionId)) {
      sessions.set(sessionId, {
        id: sessionId,
        shortId: shortId(sessionId),
        projectPath: filePath,
        projectLabel: projectLabel(filePath),
        firstPrompt: null,
        model,
        modelHistory: new Set([model]),
        isSidechain,
        tokens: { input: 0, output: 0, cacheRead: 0, cacheCreate: 0 },
        events: [],
        lastSeen: ts,
      });
    }

    const sess = sessions.get(sessionId);
    sess.model = model;
    sess.modelHistory.add(model);
    sess.lastSeen = Math.max(sess.lastSeen, ts);
    sess.tokens.input      += inputTok;
    sess.tokens.output     += outputTok;
    sess.tokens.cacheRead  += cacheRead;
    sess.tokens.cacheCreate += cacheCreate;
    sess.events.push({ ts, input: inputTok, output: outputTok, cacheRead, cacheCreate });

    // Keep only last 100 events per session for sparklines
    if (sess.events.length > 100) sess.events.shift();

    // Global rate tracking
    globalEvents.push({ ts, total: totalTok });

    // Daily token accumulation for weekly gauge
    const dateKey = new Date(ts).toISOString().slice(0, 10); // 'YYYY-MM-DD'
    dailyTokens.set(dateKey, (dailyTokens.get(dateKey) || 0) + totalTok);
  }

  // Capture first prompts from user messages (secondary pass)
  for (const line of lines) {
    let obj;
    try { obj = JSON.parse(line); } catch { continue; }
    if (obj.type !== 'user') continue;
    const sessionId = obj.sessionId;
    if (!sessionId || !sessions.has(sessionId)) continue;
    const sess = sessions.get(sessionId);
    if (sess.firstPrompt) continue;
    const content = obj.message?.content;
    if (typeof content === 'string' && content.length > 0 && !content.startsWith('<')) {
      sess.firstPrompt = content.slice(0, 80);
    }
  }
}

function tailFile(filePath) {
  const offset = fileOffsets.get(filePath) || 0;
  let stat;
  try { stat = fs.statSync(filePath); } catch { return; }
  if (stat.size <= offset) return;

  const fd = fs.openSync(filePath, 'r');
  const buf = Buffer.alloc(stat.size - offset);
  fs.readSync(fd, buf, 0, buf.length, offset);
  fs.closeSync(fd);

  fileOffsets.set(filePath, stat.size);
  processNewLines(filePath, buf.toString('utf8'));
}

// Initial full parse of a file
function parseFullFile(filePath) {
  let content;
  try { content = fs.readFileSync(filePath, 'utf8'); } catch { return; }
  fileOffsets.set(filePath, Buffer.byteLength(content, 'utf8'));
  processNewLines(filePath, content);

  // Also grab first prompts from the full file
  const lines = content.split('\n').filter(Boolean);
  for (const line of lines) {
    let obj;
    try { obj = JSON.parse(line); } catch { continue; }
    if (obj.type !== 'user') continue;
    const sessionId = obj.sessionId;
    if (!sessionId || !sessions.has(sessionId)) continue;
    const sess = sessions.get(sessionId);
    if (sess.firstPrompt) continue;
    const content2 = obj.message?.content;
    if (typeof content2 === 'string' && content2.length > 0 && !content2.startsWith('<')) {
      sess.firstPrompt = content2.slice(0, 80);
    }
  }
}

// ─── File Watcher ────────────────────────────────────────────────────────────

function startWatcher(wss) {
  const watcher = chokidar.watch(`${PROJECTS_DIR}/**/*.jsonl`, {
    persistent: true,
    ignoreInitial: false,
    awaitWriteFinish: { stabilityThreshold: 100, pollInterval: 50 },
  });

  watcher.on('add', (filePath) => {
    parseFullFile(filePath);
    broadcast(wss, buildState());
  });

  watcher.on('change', (filePath) => {
    tailFile(filePath);
    pruneGlobalEvents();
    broadcast(wss, buildState());
  });

  watcher.on('error', (err) => console.error('Watcher error:', err));
  console.log(`Watching ${PROJECTS_DIR}`);
}

// ─── claude.ai Utilization API ───────────────────────────────────────────────

async function fetchUtilization() {
  if (!SESSION_KEY || !ORG_ID) return;

  const url = `https://claude.ai/api/organizations/${ORG_ID}/usage`;
  try {
    const res = await fetch(url, {
      headers: {
        Cookie: `sessionKey=${SESSION_KEY}`,
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'Origin': 'https://claude.ai',
        'Referer': 'https://claude.ai/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'anthropic-client-platform': 'web_claude_ai',
      },
    });
    if (!res.ok) {
      const body = await res.text().catch(() => '');
      throw new Error(`HTTP ${res.status} — ${body.slice(0, 120)}`);
    }
    const json = await res.json();
    const fiveHour  = json.five_hour   || {};
    const sevenDay  = json.seven_day   || {};

    // Per-model seven-day keys: seven_day_opus, seven_day_sonnet, etc.
    const models = {};
    const modelKeyPrefix = 'seven_day_';
    const skipKeys = new Set(['seven_day_oauth_apps', 'seven_day_cowork']);
    for (const [key, val] of Object.entries(json)) {
      if (!key.startsWith(modelKeyPrefix) || skipKeys.has(key) || !val) continue;
      const modelName = key.slice(modelKeyPrefix.length); // 'opus', 'sonnet', etc.
      models[modelName] = { utilization: val.utilization ?? null, resetsAt: val.resets_at ?? null };
    }

    utilizationData = {
      fiveHour: {
        utilization: fiveHour.utilization ?? null,
        resetsAt:    fiveHour.resets_at   ?? null,
      },
      weekly: {
        utilization: sevenDay.utilization ?? null,
        resetsAt:    sevenDay.resets_at   ?? null,
      },
      models,
      monthly: json.extra_usage?.is_enabled ? {
        utilization:  Math.round(json.extra_usage.utilization ?? 0),
        usedCredits:  json.extra_usage.used_credits   ?? null,
        monthlyLimit: json.extra_usage.monthly_limit  ?? null,
      } : null,
      fetchedAt: Date.now(),
    };
  } catch (err) {
    console.warn('Usage API fetch failed:', err.message);
  }
}

// ─── State Serialization ─────────────────────────────────────────────────────

function buildState() {
  const rate = computeRate();

  const sessionList = [...sessions.values()]
    .sort((a, b) => b.lastSeen - a.lastSeen)
    .map(s => ({
      id: s.shortId,
      fullId: s.id,
      projectLabel: s.projectLabel,
      firstPrompt: s.firstPrompt || '(no prompt captured)',
      model: s.model,
      models: [...s.modelHistory],
      isSidechain: s.isSidechain,
      tokens: s.tokens,
      totalTokens: tokensTotal(s.tokens),
      lastSeen: s.lastSeen,
      // Last 20 events for mini sparkline
      recentEvents: s.events.slice(-20).map(e => ({
        ts: e.ts,
        total: e.input + e.output + e.cacheRead + e.cacheCreate,
      })),
    }));

  // Model breakdown across all sessions
  const modelBreakdown = {};
  for (const s of sessions.values()) {
    const key = s.model;
    modelBreakdown[key] = (modelBreakdown[key] || 0) + tokensTotal(s.tokens);
  }

  // 10-minute history buckets (30-second each) for rate chart
  const now = Date.now();
  const bucketCount = 20;
  const bucketSize = 30_000;
  const rateBuckets = Array.from({ length: bucketCount }, (_, i) => {
    const bucketStart = now - (bucketCount - i) * bucketSize;
    const bucketEnd   = bucketStart + bucketSize;
    const total = globalEvents
      .filter(e => e.ts >= bucketStart && e.ts < bucketEnd)
      .reduce((s, e) => s + e.total, 0);
    return { ts: bucketEnd, tokens: total };
  });

  return {
    type: 'state',
    ts: now,
    utilization: utilizationData,
    hasUsageApi: !!(SESSION_KEY && ORG_ID),
    rate,
    sessions: sessionList,
    modelBreakdown,
    rateBuckets,
    totalSessions: sessions.size,
    totalTokensAllTime: sessionList.reduce((s, sess) => s + sess.totalTokens, 0),
  };
}

// ─── WebSocket ───────────────────────────────────────────────────────────────

function broadcast(wss, data) {
  const msg = JSON.stringify(data);
  for (const client of wss.clients) {
    if (client.readyState === 1) client.send(msg);
  }
}

// ─── Express Server ──────────────────────────────────────────────────────────

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// GET /api/config — current credentials (session key masked)
app.get('/api/config', (req, res) => {
  res.json({
    orgId:            ORG_ID || '',
    sessionKeyMasked: SESSION_KEY ? SESSION_KEY.slice(0, 24) + '…' : '',
    hasConfig:        !!(SESSION_KEY && ORG_ID),
  });
});

// POST /api/config — update credentials, persist to .env, re-fetch
app.post('/api/config', async (req, res) => {
  const { sessionKey, orgId } = req.body || {};
  if (!sessionKey || !orgId) {
    return res.status(400).json({ error: 'sessionKey and orgId are required' });
  }
  SESSION_KEY = sessionKey.trim();
  ORG_ID      = orgId.trim();
  try {
    writeEnv({ CLAUDE_SESSION_KEY: SESSION_KEY, CLAUDE_ORG_ID: ORG_ID });
  } catch (err) {
    console.warn('Could not write .env:', err.message);
  }
  await fetchUtilization();
  broadcast(wss, buildState());
  res.json({ ok: true });
});

const server = http.createServer(app);
const wss = new WebSocketServer({ server });

wss.on('connection', (ws) => {
  console.log('Dashboard connected');
  ws.send(JSON.stringify(buildState()));
  ws.on('close', () => console.log('Dashboard disconnected'));
});

// ─── Boot ─────────────────────────────────────────────────────────────────────

server.listen(PORT, () => {
  console.log(`Claude Usage Monitor running at http://localhost:${PORT}`);
  if (!SESSION_KEY) console.warn('  CLAUDE_SESSION_KEY not set — 5-hour utilization gauge will be disabled');
  if (!ORG_ID)      console.warn('  CLAUDE_ORG_ID not set — 5-hour utilization gauge will be disabled');
});

startWatcher(wss);

// Initial utilization fetch, then poll
fetchUtilization();
setInterval(async () => {
  await fetchUtilization();
  broadcast(wss, buildState());
}, USAGE_POLL_MS);

// Heartbeat so iframe knows it's alive
setInterval(() => broadcast(wss, { type: 'ping', ts: Date.now() }), 5000);
