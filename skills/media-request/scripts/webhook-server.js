#!/usr/bin/env node
/**
 * Radarr Webhook Server
 * Listens for download completion events and notifies requesting sessions
 * 
 * Usage: node webhook-server.js [port]
 * Default port: 9876
 */

const http = require('http');
const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

const PORT = process.argv[2] || 9876;
const PENDING_FILE = path.join(__dirname, '../data/pending-requests.json');
const SCRIPTS_DIR = __dirname;

// Ensure data directory exists
const dataDir = path.dirname(PENDING_FILE);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Load/save pending requests
function loadPending() {
  try {
    return JSON.parse(fs.readFileSync(PENDING_FILE, 'utf8'));
  } catch {
    return {};
  }
}

function savePending(data) {
  fs.writeFileSync(PENDING_FILE, JSON.stringify(data, null, 2));
}

// Check Jellyfin availability
function checkJellyfin(title, year) {
  try {
    const cmd = `${SCRIPTS_DIR}/check-jellyfin.sh "${title}" ${year || ''}`;
    const result = execSync(cmd, { encoding: 'utf8', timeout: 15000 });
    return JSON.parse(result.trim());
  } catch (e) {
    return { status: 'ERROR', message: e.message };
  }
}

// Send notification via OpenClaw sessions_send
function notifySession(sessionKey, message) {
  // This will be called by the parent process or via cron
  // For now, write to a notification queue file
  const notifyFile = path.join(dataDir, 'notifications.jsonl');
  const notification = JSON.stringify({
    timestamp: new Date().toISOString(),
    sessionKey,
    message
  }) + '\n';
  fs.appendFileSync(notifyFile, notification);
  console.log(`[NOTIFY] Queued for ${sessionKey}: ${message.event || message}`);
}

// Handle Radarr webhook
function handleRadarrWebhook(body) {
  const eventType = body.eventType;
  console.log(`[RADARR] Event: ${eventType}`);

  if (eventType === 'Download' || eventType === 'MovieFileImported') {
    const movie = body.movie || {};
    const title = movie.title;
    const year = movie.year;
    const radarrId = movie.id;
    const quality = body.movieFile?.quality?.quality?.name || 'Unknown';

    console.log(`[RADARR] Download complete: ${title} (${year}) - ${quality}`);

    // Check if this was a pending request
    const pending = loadPending();
    const request = pending[radarrId];

    // Verify in Jellyfin
    const jellyfin = checkJellyfin(title, year);

    const notification = {
      event: 'download_complete',
      title,
      year,
      radarrId,
      quality,
      jellyfinId: jellyfin.jellyfinId || null,
      jellyfinStatus: jellyfin.status,
      message: `${title} (${year}) is ready to watch! 🍿`,
      requestedBy: request?.requestedBy || 'Unknown'
    };

    if (request?.replySession) {
      notifySession(request.replySession, notification);
      // Remove from pending
      delete pending[radarrId];
      savePending(pending);
    } else {
      // No tracked request, just log
      console.log(`[INFO] No pending request for radarrId ${radarrId}`);
    }

    return { status: 'ok', processed: true };
  }

  if (eventType === 'Grab') {
    const movie = body.movie || {};
    console.log(`[RADARR] Grabbed: ${movie.title} (${movie.year})`);
    return { status: 'ok', event: 'grab_logged' };
  }

  return { status: 'ok', event: 'ignored' };
}

// HTTP server
const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/radarr') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const result = handleRadarrWebhook(data);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (e) {
        console.error('[ERROR]', e.message);
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
  } else if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', pending: Object.keys(loadPending()).length }));
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, () => {
  console.log(`[WEBHOOK] Radarr webhook server listening on port ${PORT}`);
  console.log(`[WEBHOOK] Endpoints: POST /radarr, GET /health`);
});
