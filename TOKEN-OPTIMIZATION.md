# TOKEN-OPTIMIZATION.md - Cost Management Strategy

*Based on expert OpenClaw optimization guide - 2026-03-01*

## 🎯 Immediate Actions

### 1. Model Strategy
- **Switch to haiku for routine tasks** (heartbeats, simple requests)
- **Use sonnet for complex reasoning** (planning, debugging)
- **Reserve opus for deep work** (research, major projects)

### 2. Heartbeat Optimization  
- **Current:** Every 30 min with haiku (but context loads ALL session history)
- **Action:** Reduce heartbeat checks, focus on essential monitoring only
- **Alternative:** Move routine monitoring to n8n workflows

### 3. Session Management
- **Compress when >100k tokens:** Use `/compact` command
- **Session handoffs:** Use temporary.md for clean session transfers  
- **Regular audits:** Weekly `/status` checks

### 4. Memory Architecture
- **Daily files:** Keep (4K each, manageable)
- **MEMORY.md:** Monitor for bloat (currently 8K - good)
- **Separate concerns:** Move logs to database vs. markdown files

### 5. Response Efficiency
- **Concise by default:** 1-2 paragraphs unless asked for detail
- **Skip narration:** Don't announce "I'm checking..." actions
- **Sub-agents for big tasks:** Keep main context clean

## 📊 Monitoring Dashboard

### Weekly File Size Check
```bash
# Monitor core files
du -h ~/clawd/{AGENTS,SOUL,MEMORY,TOOLS}.md ~/clawd/memory/journal.md
```

### Session Health Check  
```bash
# Use /status command to check:
# - Token usage
# - Model efficiency  
# - Context bloat
```

### Cost Tracking
- Set daily spend limits ($5/day recommended)
- Review weekly efficiency 
- Model usage analysis

## 🔄 n8n Migration Targets

**Move these FROM AI cron TO n8n:**
- Weather checks (use free weather APIs)
- News summaries (RSS + simple formatting)
- Basic health monitoring (system stats)
- Routine notifications

**Keep in AI cron:**
- Complex decision making
- Context-aware alerts
- Multi-system coordination

## 📁 File Structure Optimization

```
memory/
├── daily/          # YYYY-MM-DD.md files
├── projects/       # Project-specific contexts  
├── logs/          # Database entries (not .md)
└── archive/       # Compressed old memories
```

## 🚀 Success Metrics

- **Session tokens:** Keep <100k without compaction
- **File sizes:** Core files <20K each
- **Model efficiency:** Right model for right task
- **Cost control:** Stay within daily limits
- **Response quality:** Concise but complete

---

*Implementation: Start with model strategy, then session hygiene, finally file optimization*