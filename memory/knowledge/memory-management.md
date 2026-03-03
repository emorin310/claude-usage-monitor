# Memory Management Knowledge Base

## Overview
Advanced memory management system implemented 2026-03-01 combining structured folders, SQLite database, and organized project tracking.

## Architecture

### 1. Structured Folders ✅
```
memory/
├── daily/           # YYYY-MM-DD.md files (session logs)
├── projects/        # Active project tracking
├── preferences/     # Agent behavior configuration  
├── knowledge/       # Research and learning notes
└── database/        # SQLite for structured data
```

### 2. SQLite Database ✅
**Location:** `memory/database/memory.db`

**Tables:**
- `quality_queue` - Movie quality upgrade tracking (5 records)
- `council_state` - Council communications state (4 thread types)  
- `media_library` - Media metadata (future expansion)
- `system_health` - Component health tracking (5 components)
- `interbot_messages` - Inter-bot communication logs
- `memory_search_cache` - Built-in search optimization

**Benefits:**
- Zero API costs (no embedding models)
- Precise querying vs. fuzzy vector search  
- Portable (single .db file)
- Session-persistent data
- Fast structured data access

### 3. Query Interface ✅
**Script:** `scripts/query-memory.js`
**Usage:** 
```bash
node query-memory.js quality_queue
node query-memory.js quality_queue "status = 'queued'"
node query-memory.js system_health "status != 'ok'"
```

## Migration Results
- **Quality upgrade queue:** 5 movies migrated (3 HIGH, 1 MEDIUM, 1 LOW priority)
- **Council state:** 4 thread types (announcements: 22, handoffs: 12, etc.)
- **System health:** 5 components (all "ok" status except token_optimization: "active")
- **Project files:** 3 structured project documents created

## Built-in Memory Search (Future)
**Requirements:**
- Configure Gemini API key for embeddings (available: `AIzaSyC470rdmUp52ocg_4t-stDwautlcoP-kUA`)
- Enable `memory_search` tool
- Test cost/benefit vs. SQLite approach

**Use cases:**
- Natural language queries across markdown files
- Cross-reference between daily logs and projects
- Preference recall and behavior learning

## MEM0 Plugin (Evaluation)
**Plugin:** `@mem0/openclaw-mem0`
**Features:** Automated vector-based memory extraction
**Evaluation criteria:** Cost vs. current methods, maintenance overhead

## Best Practices

### When to Use Each Method
- **SQLite:** Structured data requiring precise queries (quality queues, health status)
- **Markdown files:** Human-readable project notes, daily logs, preferences
- **Built-in search:** Cross-file natural language queries (when cost-effective)
- **MEM0:** Automated extraction (evaluate against manual curation)

### Maintenance
- **Weekly file monitoring:** Check sizes with `file-size-monitor.sh`
- **Database cleanup:** Archive completed projects periodically
- **Query optimization:** Monitor performance, add indexes as needed
- **Cost tracking:** Compare SQLite efficiency vs. vector search costs

## Integration with Token Optimization
- **Context reduction:** SQLite queries load only relevant data vs. full JSON files
- **Structured access:** Precise data retrieval reduces session bloat  
- **Model efficiency:** Match query complexity to model capability
- **Cost savings:** Database queries avoid repeated context loading

## Success Metrics
- ✅ **Migration completed:** All structured data in SQLite
- ✅ **Organization improved:** Clear project/preference/knowledge separation
- ✅ **Query interface:** Direct database access without session overhead
- 📊 **Performance:** Monitor query speed vs. file parsing
- 💰 **Cost impact:** Measure context size reduction

*This system provides the foundation for efficient, scalable memory management while maintaining transparency and cost optimization.*