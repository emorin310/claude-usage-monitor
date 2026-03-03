# MEMORY-STRATEGY.md - Advanced Memory Management Implementation

## 🎯 Hybrid Approach: Structured + SQLite + Built-in Search

### Current State Analysis
- **Memory files:** Healthy sizes (4-8KB each)
- **Structure:** Basic daily logs + JSON state files
- **Challenge:** Growing complexity of structured data (quality queues, council state, etc.)

## 🏗️ Implementation Plan

### Phase 1: Enhanced Structured Folders ✅ ACTIVE
```
memory/
├── daily/           # YYYY-MM-DD.md files (keep current approach)
├── projects/        # Ongoing projects & workflows
│   ├── quality-upgrades.md
│   ├── imessage-integration.md
│   └── token-optimization.md
├── preferences/     # Agent behavior & style guides
│   ├── communication.md
│   └── task-handling.md
├── knowledge/       # Research & learning
│   ├── openclaw-features.md
│   ├── token-optimization.md
│   └── memory-methods.md
└── database/        # SQLite for structured data
```

### Phase 2: SQLite for Structured Data 🎯 PRIORITY
**Perfect for our use cases:**
- **Quality upgrade queues** (movie title, resolution, priority, status)
- **Council communications** (thread counts, task states, response tracking)
- **Inter-bot message logs** (sender, timestamp, action type, status)
- **Media library metadata** (title, year, quality, file size, IMDB links)
- **System health tracking** (component, status, last_check, alerts)

**Benefits:**
- ✅ **Zero API costs** (no embedding models needed)
- ✅ **Precise querying** vs. fuzzy vector search
- ✅ **Portable** (single .db file)
- ✅ **Fast lookups** for structured data
- ✅ **Session-persistent** data

### Phase 3: Built-in Memory Search (Optional)
**Requirements:**
- Configure Gemini API key for embeddings (already have: `AIzaSyC470rdmUp52ocg_4t-stDwautlcoP-kUA`)
- Enable `memory_search` tool usage
- Test cost/benefit ratio

**Use cases:**
- Natural language queries across all memory files
- Cross-reference between daily logs and project notes
- Preference recall ("How did I handle X last time?")

### Phase 4: MEM0 Plugin (Future Consideration)
**Evaluation criteria:**
- Cost analysis vs. current methods
- Maintenance overhead
- Integration with existing workflows

## 🚀 Immediate Actions

### 1. Create Enhanced Folder Structure
```bash
mkdir -p ~/clawd/memory/{projects,preferences,knowledge,database}
```

### 2. Migrate Current Data
- Move `quality-upgrade-queue.json` → SQLite table
- Move `council-state.json` → SQLite table  
- Create project-specific markdown files

### 3. SQLite Schema Design
- **quality_queue** table (id, title, year, current_quality, target_quality, status, priority, issues)
- **council_state** table (thread_type, count, last_updated, alerts)
- **media_library** table (title, year, quality, file_size, imdb_id, jellyfin_url, status)
- **system_health** table (component, status, last_check, details)

## 💰 Cost Impact
- **Structured folders:** Zero cost, pure efficiency gain
- **SQLite:** Zero API cost, reduces context loading
- **Built-in search:** Minimal cost (Gemini embeddings ~$0.00001/query)
- **Expected savings:** 20-40% reduction in context size for structured data queries

## 📊 Success Metrics
- Faster data retrieval for structured queries
- Reduced session context size
- Better organization of project knowledge
- Maintained transparency (can still read all data)

---
*Next: Implement Phase 1 folder structure and Phase 2 SQLite migration*