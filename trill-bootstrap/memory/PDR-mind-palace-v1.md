# PDR: Mind Palace Architecture v1.0
**Author:** Magi | **Date:** 2026-01-29 | **Status:** DRAFT

---

## 1. Problem Statement

### Current Pain Points
- **Context Bloat:** Loading MEMORY.md + daily logs + workspace files can overwhelm context windows
- **Unstructured Growth:** Memory files grow unbounded without clear organization
- **Fragile Recovery:** After a "factory reset" or new session, rebuilding context is slow and lossy
- **Search Friction:** Finding specific info requires loading entire files
- **No Versioning:** Can't track what changed or roll back

### Goals
1. **Resilient** - Survive crashes, resets, model switches
2. **Portable** - Pure files, no external dependencies required
3. **Efficient** - Lazy-load only what's needed
4. **Queryable** - Fast semantic + keyword search
5. **Evolvable** - Easy to add categories, refactor structure
6. **Human-Readable** - Eric can edit directly if needed

---

## 2. Architecture Options

### Option A: Hierarchical .md with Index
```
mind-palace/
├── INDEX.md              # Master TOC + load instructions
├── SCHEMA.md             # Structure definitions
│
├── identity/
│   ├── soul.md           # Persona, voice, boundaries
│   ├── preferences.md    # Likes, dislikes, style
│   └── rules.md          # Operating constraints
│
├── relationships/
│   ├── family.md         # Eric's family tree + notes
│   ├── contacts.md       # Phone numbers, emails, mappings
│   └── agents.md         # Marvin, Cray, council info
│
├── knowledge/
│   ├── tools.md          # Tool configs, API keys, endpoints
│   ├── skills.md         # Learned procedures
│   ├── systems.md        # Homelab, devices, infrastructure
│   └── services.md       # Subscriptions, accounts
│
├── schedules/
│   ├── routines.md       # Daily/weekly patterns
│   ├── recurring.md      # Birthdays, anniversaries
│   └── cron-jobs.md      # Automated task reference
│
├── runbooks/
│   ├── morning-briefing.md
│   ├── appointment-flow.md
│   ├── council-protocol.md
│   └── emergency-procedures.md
│
├── logs/
│   ├── 2026-01-29.md     # Daily activity logs
│   └── archive/          # Old logs (compressed/summarized)
│
└── state/
    ├── active-context.json   # What's currently relevant
    ├── council-state.json    # Multi-agent coordination
    └── pending-actions.json  # Queued tasks/approvals
```

**Pros:** Pure markdown, human-editable, git-friendly, works with memory_search
**Cons:** No complex queries, relies on semantic search quality

---

### Option B: JSON + Markdown Hybrid
```
mind-palace/
├── index.json            # Structured TOC with metadata
├── schema.json           # JSON Schema definitions
│
├── data/
│   ├── contacts.json     # Structured: {name, phone, relation, ...}
│   ├── schedules.json    # Structured: recurring events
│   ├── tools.json        # API configs, endpoints
│   └── state.json        # Current state machine
│
├── context/
│   ├── soul.md           # Narrative persona
│   ├── relationships.md  # Rich context about people
│   └── knowledge.md      # Learned wisdom
│
└── runbooks/
    └── *.md              # Procedural guides
```

**Pros:** Best of both - structured queries + rich narrative
**Cons:** Dual maintenance, need JSON parsing in prompts

---

### Option C: SQLite Backend
```
mind-palace/
├── palace.db             # SQLite database
├── context/              # .md files for narrative
└── runbooks/             # Procedural guides
```

**Schema:**
```sql
CREATE TABLE contacts (id, name, phone, email, relation, notes);
CREATE TABLE events (id, title, datetime, location, recurrence);
CREATE TABLE knowledge (id, category, key, value, updated_at);
CREATE TABLE logs (id, date, category, content);
```

**Pros:** Real queries, ACID, portable single file, handles scale
**Cons:** Need SQL execution, less human-editable, tooling dependency

---

### Option D: MongoDB (via MCP or REST)
**Pros:** Powerful queries, scales infinitely, flexible schema
**Cons:** External dependency, not portable, overkill for current needs

---

## 3. Recommendation: **Option A + Selective JSON (Hybrid Lite)**

### Rationale
1. **Start simple** - Pure .md works with existing memory_search
2. **Add JSON for structured data** - contacts.json, schedules.json where queries matter
3. **Keep narrative in .md** - Soul, relationships, knowledge stay human-readable
4. **INDEX.md as brain stem** - Always loaded, tells me what to load next
5. **Upgrade path** - Can migrate to SQLite later if needed

### Load Strategy
```
Session Start:
1. ALWAYS load: INDEX.md, identity/soul.md, identity/rules.md
2. ON DEMAND: Use memory_search to find relevant files
3. CACHE: Keep active-context.json updated with current session needs
4. PRUNE: Summarize old logs, archive quarterly
```

---

## 4. Implementation Plan

### Phase 1: Foundation (This Week)
- [ ] Create mind-palace/ directory structure
- [ ] Migrate MEMORY.md → split into categories
- [ ] Create INDEX.md with load instructions
- [ ] Move USER.md content → relationships/family.md + contacts.json
- [ ] Move TOOLS.md → knowledge/tools.md

### Phase 2: Runbooks (Next Week)
- [ ] Document morning-briefing workflow
- [ ] Document appointment-detection flow
- [ ] Document council-protocol
- [ ] Document heartbeat procedures

### Phase 3: State Management
- [ ] Design active-context.json schema
- [ ] Implement context pruning rules
- [ ] Create log archival process

### Phase 4: Optimization
- [ ] Evaluate SQLite migration if JSON gets unwieldy
- [ ] Add embeddings index for faster semantic search
- [ ] Consider MCP server for structured queries

---

## 5. Open Questions for Eric

1. **Storage location:** Keep in `~/clawd-magi/mind-palace/` or separate repo?
2. **Backup strategy:** Git commits? Syncthing to Marvin's domain?
3. **Access control:** Any files that should be encrypted/protected?
4. **Log retention:** How long to keep daily logs before archiving?
5. **Shared data:** What should be accessible to Marvin/Cray vs. Magi-only?

---

## 6. Success Metrics

- [ ] Cold start time < 30 seconds to operational
- [ ] Context window usage < 50% for routine tasks
- [ ] Can fully rebuild from files after reset
- [ ] No lost information during model switches
- [ ] Eric can understand/edit structure without help

---

*Next step: Review this PDR, pick an option, start Phase 1.*
