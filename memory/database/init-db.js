#!/usr/bin/env node
// Initialize OpenClaw Memory SQLite Database
// Usage: node init-db.js

const fs = require('fs');
const path = require('path');

// Use Node.js built-in SQLite (available in Node 22+) or fallback
let Database;
try {
  // Try Node.js built-in SQLite (Node 22.5+)
  Database = require('node:sqlite').DatabaseSync;
} catch (e) {
  console.log('Node.js built-in SQLite not available, checking for better-sqlite3...');
  try {
    // Fallback to better-sqlite3 if available
    Database = require('better-sqlite3');
  } catch (e2) {
    console.error('No SQLite library found. Please install better-sqlite3:');
    console.error('npm install -g better-sqlite3');
    process.exit(1);
  }
}

const dbPath = path.join(__dirname, 'memory.db');
const schemaPath = path.join(__dirname, 'init-schema.sql');

console.log('🗄️ Initializing OpenClaw Memory Database...');

try {
  // Read the schema file
  const schema = fs.readFileSync(schemaPath, 'utf8');
  
  // Initialize database
  const db = new Database(dbPath);
  
  // Execute schema
  const statements = schema.split(';').filter(stmt => stmt.trim().length > 0);
  
  for (const stmt of statements) {
    if (stmt.trim()) {
      db.exec(stmt.trim() + ';');
    }
  }
  
  console.log('✅ Database initialized successfully!');
  console.log(`📍 Location: ${dbPath}`);
  
  // Test the database
  const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
  console.log('📋 Created tables:', tables.map(t => t.name).join(', '));
  
  db.close();
  
} catch (error) {
  console.error('❌ Database initialization failed:', error.message);
  process.exit(1);
}

console.log('🎯 Database ready for structured memory management!');