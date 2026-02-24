#!/usr/bin/env node
const crypto = require('crypto');
const https = require('https');
const fs = require('fs');

const TOKEN = '1425e4eff8e83fc361d6bdd4ac9922c34d5089db';
const STATE_FILE = '/Users/eric/clawd-magi/mind-palace/state/task-state.json';
const THRESHOLD_DAYS = 7;

function hashTask(t) {
  const data = JSON.stringify({
    content: t.content,
    description: t.description,
    labels: t.labels,
    priority: t.priority,
    comment_count: t.comment_count,
    due: t.due
  });
  return crypto.createHash('md5').update(data).digest('hex').slice(0, 8);
}

function daysSince(isoDate) {
  return (Date.now() - new Date(isoDate).getTime()) / (1000 * 60 * 60 * 24);
}

const options = {
  hostname: 'api.todoist.com',
  path: '/api/v1/tasks',
  headers: { 'Authorization': `Bearer ${TOKEN}` }
};

https.get(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    const body = JSON.parse(data);
    const tasks = Array.isArray(body) ? body : (body.results || []);
    const now = new Date().toISOString();
    
    // Load existing state
    let state;
    try {
      state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    } catch (e) {
      console.error('❌ No task-state.json found. Run init-task-state.js first.');
      process.exit(1);
    }
    
    const stagnant = [];
    const updated = [];
    const newTasks = [];
    
    tasks.forEach(t => {
      const hash = hashTask(t);
      const existing = state.taskActivity[t.id];
      
      if (!existing) {
        // New task
        state.taskActivity[t.id] = {
          content: t.content.slice(0, 60),
          lastUpdated: now,
          lastHash: hash
        };
        newTasks.push(t.content.slice(0, 50));
      } else if (existing.lastHash !== hash) {
        // Task changed
        existing.lastUpdated = now;
        existing.lastHash = hash;
        existing.content = t.content.slice(0, 60);
        updated.push(t.content.slice(0, 50));
      } else {
        // No change - check if stagnant
        const days = daysSince(existing.lastUpdated);
        if (days >= THRESHOLD_DAYS) {
          stagnant.push({
            id: t.id,
            content: t.content.slice(0, 60),
            days: Math.floor(days),
            labels: t.labels,
            url: t.url
          });
        }
      }
    });
    
    // Remove deleted tasks
    const currentIds = new Set(tasks.map(t => t.id));
    const deleted = [];
    for (const id of Object.keys(state.taskActivity)) {
      if (!currentIds.has(id)) {
        deleted.push(state.taskActivity[id].content);
        delete state.taskActivity[id];
      }
    }
    
    state.lastScanned = now;
    state.totalTasks = tasks.length;
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
    
    // Output report
    console.log('📊 **Task Stagnation Report**');
    console.log(`Scanned: ${tasks.length} tasks | Threshold: ${THRESHOLD_DAYS} days\n`);
    
    if (stagnant.length > 0) {
      console.log(`🪨 **Stagnant (${stagnant.length}):**`);
      stagnant.sort((a, b) => b.days - a.days).slice(0, 20).forEach(t => {
        const labels = t.labels.length ? ` [${t.labels.join(', ')}]` : '';
        console.log(`  - ${t.content} (${t.days}d)${labels}`);
      });
      if (stagnant.length > 20) console.log(`  ... and ${stagnant.length - 20} more`);
    } else {
      console.log('✅ No stagnant tasks!');
    }
    
    if (updated.length) console.log(`\n🔄 Updated: ${updated.length}`);
    if (newTasks.length) console.log(`➕ New: ${newTasks.length}`);
    if (deleted.length) console.log(`🗑️ Removed: ${deleted.length}`);
    
    // JSON output for programmatic use
    if (process.argv.includes('--json')) {
      console.log('\n---JSON---');
      console.log(JSON.stringify({ stagnant, updated: updated.length, newTasks: newTasks.length }, null, 2));
    }
  });
}).on('error', console.error);
