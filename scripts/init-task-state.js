#!/usr/bin/env node
const crypto = require('crypto');
const https = require('https');
const fs = require('fs');

const TOKEN = '1425e4eff8e83fc361d6bdd4ac9922c34d5089db';
const OUTPUT = '/Users/eric/clawd-magi/mind-palace/state/task-state.json';

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
    
    const taskActivity = {};
    tasks.forEach(t => {
      taskActivity[t.id] = {
        content: t.content.slice(0, 60),
        lastUpdated: now,
        lastHash: hashTask(t)
      };
    });
    
    const state = {
      version: 1,
      lastScanned: now,
      stagnantThresholdDays: 7,
      totalTasks: tasks.length,
      taskActivity
    };
    
    fs.writeFileSync(OUTPUT, JSON.stringify(state, null, 2));
    console.log(`✅ Created ${OUTPUT} with ${tasks.length} tasks`);
  });
}).on('error', console.error);
