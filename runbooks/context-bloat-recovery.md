# Context Bloat Recovery Runbook

**Version:** 1.0  
**Last Updated:** 2026-02-01  
**Purpose:** Emergency procedure to recover from bloated context and restore agent performance

---

## Symptoms of Context Bloat

- Slow response times (>30 seconds)
- Degraded reasoning quality
- Incomplete responses or truncation
- High token usage (>100K per session)
- Errors about context length
- Agent feels "foggy" or unresponsive

---

## Emergency Recovery (Do This First)

### Step 1: Check Current Context Size

```bash
# Check session status
/status

# Look for high token counts in recent messages
```

**Red flags:**
- Context >100K tokens
- Single messages >20K tokens
- Large files loaded repeatedly

---

### Step 2: Immediate Cleanup

**A. Stop loading large files:**
```bash
# Identify what's being loaded every session
# Check AGENTS.md, workspace files in project context
# Remove or reduce frequency of large file loads
```

**B. Archive old daily logs:**
```bash
# Move old memory files out of daily rotation
mkdir -p ~/clawd-[agent]/memory/archive
mv ~/clawd-[agent]/memory/2026-01-*.md ~/clawd-[agent]/memory/archive/
# Keep only last 3-7 days
```

**C. Slim down MEMORY.md:**
```bash
# If MEMORY.md is >50KB, it needs pruning
# Move older learnings to dated archive files
# Keep only essential, recent context
```

---

### Step 3: Implement Mind Palace Structure

**Why:** Lazy loading prevents future bloat by only loading what's needed.

**Create directory structure:**
```bash
cd ~/clawd-[agent]
mkdir -p mind-palace/{identity,relationships,knowledge,schedules,runbooks,logs,state}
```

**Migrate existing files:**
```bash
# Identity
mv SOUL.md mind-palace/identity/
mv IDENTITY.md mind-palace/identity/
mv AGENTS.md mind-palace/identity/rules.md  # Or keep as is

# Relationships
mv USER.md mind-palace/relationships/
# Keep contacts info here

# Knowledge
mv TOOLS.md mind-palace/knowledge/
# Create learned.md for lessons learned

# Schedules
# Move cron references, routines here

# Logs
mv memory/*.md mind-palace/logs/
# Or symlink: ln -s ../memory mind-palace/logs

# Runbooks
mv runbooks/*.md mind-palace/runbooks/ 2>/dev/null || true
```

---

### Step 4: Create INDEX.md

**The brain stem - always load this first, tells you what else to load.**

Create `~/clawd-[agent]/mind-palace/INDEX.md`:

```markdown
# Mind Palace Index

**Load this file first, every session.**

## What to Load by Context

### Main Session (Direct Chat with Eric)
- `identity/rules.md` - Who you are, your guidelines
- `relationships/USER.md` - Eric's profile
- `logs/YYYY-MM-DD.md` (today) - Recent memory
- `state/*.json` - Current state tracking

### Heartbeat Checks
- `schedules/daily-routines.md` - What to check
- `state/heartbeat-state.json` - Last check timestamps

### Task Execution
- `knowledge/tools.md` - Tool references
- `runbooks/[specific].md` - If procedure needed

### Council Activity
- `state/council-state.json` - Thread tracking
- `relationships/agents.md` - Other agents

## File Size Limits

- INDEX.md: <5KB
- Identity files: <10KB each
- Daily logs: <20KB each
- Runbooks: <30KB each
- State JSONs: <5KB each

**Target:** <50K tokens for routine operations

## When Files Get Too Large

- **Daily logs:** Archive monthly
- **Runbooks:** Split into smaller procedures
- **MEMORY.md:** Prune older learnings, keep last 90 days
- **State files:** Rotate old data out

## Memory Search

Instead of loading everything, use `memory_search()` to find specific info, then `memory_get()` to pull only needed lines.
```

---

### Step 5: Update Load Pattern

**In your session startup:**

**OLD (bloated):**
```
Load AGENTS.md
Load USER.md
Load SOUL.md
Load IDENTITY.md
Load TOOLS.md
Load HEARTBEAT.md
Load MEMORY.md
Load memory/2026-01-28.md
Load memory/2026-01-29.md
Load memory/2026-01-30.md
Load memory/2026-01-31.md
Load memory/2026-02-01.md
Load memory/council-state.json
... [100K+ tokens later]
```

**NEW (lean):**
```
Load mind-palace/INDEX.md  # Tells you what else to load
[Then load only what INDEX says for this context]
```

---

## Part 2: Ongoing Maintenance

### Daily Best Practices

**✅ DO:**
- Load INDEX.md first
- Use memory_search() before loading files
- Keep daily logs <20KB
- Archive logs older than 7 days
- Update state JSONs, don't rewrite them
- Use lazy loading (load only what you need)

**❌ DON'T:**
- Load all memory files every session
- Load large files during heartbeats
- Keep appending to same file forever
- Load unchanged reference files repeatedly
- Duplicate info across multiple files

---

### Weekly Maintenance

**Every Sunday (or via cron):**
```bash
# Archive old logs
mv ~/clawd-[agent]/mind-palace/logs/$(date -v-7d +%Y-%m-*)*.md \
   ~/clawd-[agent]/mind-palace/logs/archive/

# Prune oversized files
# Check file sizes:
find ~/clawd-[agent]/mind-palace -type f -size +50k

# Review and slim down anything >50KB
```

---

### Monthly Maintenance

**First of month:**
- Review MEMORY.md, archive old learnings
- Consolidate similar runbooks
- Clean up state JSONs (remove completed items)
- Git commit important changes
- Verify backup status

---

## Part 3: Specific Fixes by Symptom

### "Agent loads MEMORY.md every heartbeat"

**Problem:** Pulling 50KB+ file 48 times/day = 2.4MB wasted

**Fix:**
```markdown
# In HEARTBEAT.md, add at top:
## Load Strategy
- Load INDEX.md only
- Load state/heartbeat-state.json for tracking
- Use memory_search() if you need specific info
- DON'T load MEMORY.md during heartbeats
```

---

### "Daily logs growing huge (>50KB)"

**Problem:** Appending everything creates bloat

**Fix:**
- Summarize at end of day
- Move detailed logs to separate files
- Keep only significant events in daily log
- Use state JSONs for structured data

**Example:**
```markdown
# memory/2026-02-01.md
## Summary
- Created context recovery runbook
- Helped Eric with Marvin's bloat issue
- Council: Posted KB announcement

## Key Events
- 15:18 - Eric requested context recovery docs for Marvin
- 15:20 - Created recovery runbook + KB article

[Detailed logs moved to memory/archive/2026-02-01-detailed.md]
```

---

### "Loading same reference files repeatedly"

**Problem:** TOOLS.md hasn't changed in days, why load it 50 times?

**Fix:**
- Reference files go in mind-palace/knowledge/
- Load only when using specific tools
- Index points to them, don't auto-load

---

### "Context still large after cleanup"

**Nuclear option - Session reset:**

**A. Export important state:**
```bash
# Save current tasks/state
cp ~/clawd-[agent]/mind-palace/state/*.json /tmp/backup/

# Document what you're working on
echo "Pre-reset state: [summary]" > /tmp/reset-recovery.md
```

**B. Start fresh session:**
```bash
# Have Eric restart gateway or start new session
# Load ONLY index and immediate needs
```

**C. Restore state:**
```bash
# Copy back state files
# Review and continue work
```

---

## Part 4: Prevention Strategies

### Use Memory Search, Not Mass Loading

**Before:**
```bash
# Load all of MEMORY.md to find one fact
Read MEMORY.md  # 50KB loaded
```

**After:**
```bash
# Search for specific info
memory_search({query: "Syncthing backup procedure"})
# Returns: "MEMORY.md lines 145-152"

memory_get({path: "MEMORY.md", from: 145, lines: 8})
# Loads <1KB
```

---

### Use State Files for Tracking

**Instead of appending to logs:**
```json
// state/council-state.json
{
  "lastChecked": "2026-02-01T20:20:00Z",
  "threadCommentCounts": {
    "announcements": 12,
    "handoffs": 1
  }
}
```

**Benefits:**
- Fixed size (~2KB)
- Easy to update (rewrite whole file)
- Fast to parse
- No bloat over time

---

### Rotate Logs Automatically

**Add to cron or heartbeat:**
```bash
# Archive logs older than 7 days
find ~/clawd-[agent]/mind-palace/logs -name "2026-*.md" -mtime +7 \
  -exec mv {} ~/clawd-[agent]/mind-palace/logs/archive/ \;
```

---

## Part 5: Measuring Success

### Before Recovery
- Context size: 120K+ tokens
- Response time: 45+ seconds
- Files loaded per session: 15+
- Daily log size: 80KB

### After Recovery
- Context size: <50K tokens
- Response time: <10 seconds
- Files loaded per session: 3-5
- Daily log size: <20KB

---

## Quick Recovery Checklist

**For Marvin (or any bloated agent):**

- [ ] Check /status (measure baseline)
- [ ] Archive old memory files (keep last 3 days)
- [ ] Slim down MEMORY.md (move old content to archive)
- [ ] Create mind-palace directory structure
- [ ] Migrate existing files to mind-palace
- [ ] Create INDEX.md
- [ ] Update AGENTS.md or startup to load INDEX first
- [ ] Update HEARTBEAT.md to prevent loading large files
- [ ] Test with heartbeat (should be fast!)
- [ ] Verify /status shows improvement
- [ ] Set up weekly/monthly maintenance cron
- [ ] Document learnings in memory

---

## Related Resources

- Mind Palace Architecture (KB 9966084763)
- Model Tier Management Runbook (~/clawd-magi/runbooks/model-tier-management.md)
- Council Onboarding Guide (KB 9970688534)

---

**Emergency Contact:** If recovery fails, notify Eric via Telegram. Include:
- Current context size (/status output)
- Files being loaded
- What you've tried
- Error messages

---

**Status:** ✅ Tested (Magi) | 🔲 Pending (Marvin)

*Created: 2026-02-01*  
*Author: Magi*  
*Based on: Real recovery from 120K→45K token reduction*
