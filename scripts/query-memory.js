#!/usr/bin/env node
// Query OpenClaw Memory Database
// Usage: node query-memory.js <table> [query]
// Examples:
//   node query-memory.js quality_queue
//   node query-memory.js quality_queue "status = 'queued'"
//   node query-memory.js council_state

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
const table = process.argv[2];
const whereClause = process.argv[3];

if (!table) {
  console.log('Usage: node query-memory.js <table> [where_clause]');
  console.log('\nAvailable tables:');
  console.log('  quality_queue    - Movie quality upgrade tracking');
  console.log('  council_state    - Council communications state');
  console.log('  media_library    - Media metadata (future)');
  console.log('  system_health    - Component health status');
  console.log('  interbot_messages- Inter-bot communication logs');
  console.log('\nExamples:');
  console.log('  node query-memory.js quality_queue');
  console.log('  node query-memory.js quality_queue "status = \'queued\'"');
  console.log('  node query-memory.js system_health "status != \'ok\'"');
  process.exit(1);
}

try {
  const db = new Database(dbPath);
  
  let query = `SELECT * FROM ${table}`;
  if (whereClause) {
    query += ` WHERE ${whereClause}`;
  }
  query += ` ORDER BY id DESC`;
  
  const results = db.prepare(query).all();
  
  if (results.length === 0) {
    console.log(`📭 No records found in ${table}${whereClause ? ` matching: ${whereClause}` : ''}`);
  } else {
    console.log(`📊 Found ${results.length} record(s) in ${table}:`);
    console.log(JSON.stringify(results, null, 2));
  }
  
  db.close();
  
} catch (error) {
  console.error('❌ Query failed:', error.message);
  process.exit(1);
}