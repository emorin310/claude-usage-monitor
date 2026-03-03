#!/usr/bin/env node
// Update council state in SQLite database

const path = require('path');

let Database;
try {
  Database = require('node:sqlite').DatabaseSync;
} catch (e) {
  try {
    Database = require('better-sqlite3');
  } catch (e2) {
    console.error('❌ No SQLite library found');
    process.exit(1);
  }
}

const dbPath = path.join(__dirname, '..', 'memory', 'database', 'memory.db');

// Get data from command line args
const councilData = JSON.parse(process.argv[2]);
const overdueTasks = parseInt(process.argv[3]);

try {
  const db = new Database(dbPath);
  
  // Update council thread counts
  const updateCouncil = db.prepare(`
    UPDATE council_state 
    SET count = ?, last_updated = CURRENT_TIMESTAMP 
    WHERE thread_type = ?
  `);
  
  for (const [threadType, count] of Object.entries(councilData.council_threads)) {
    updateCouncil.run(count, threadType);
  }
  
  // Update system health with overdue task alert if increased
  if (overdueTasks > 1) {
    const updateHealth = db.prepare(`
      UPDATE system_health 
      SET status = 'warning', 
          details = ?, 
          last_check = CURRENT_TIMESTAMP
      WHERE component = 'todoist_council'
    `);
    
    const details = JSON.stringify({
      overdue_tasks: overdueTasks,
      needs_magi_tasks: councilData.tasks.needs_magi,
      api_token_missing: true,
      last_check: councilData.checked_at
    });
    
    updateHealth.run(details);
    
    // Insert if doesn't exist
    const insertHealth = db.prepare(`
      INSERT OR IGNORE INTO system_health (component, status, details, last_check)
      VALUES ('todoist_council', 'warning', ?, CURRENT_TIMESTAMP)
    `);
    insertHealth.run(details);
  }
  
  db.close();
  console.log(`✅ Updated council state - overdue tasks: ${overdueTasks}`);
  
} catch (error) {
  console.error('❌ Update failed:', error.message);
  process.exit(1);
}