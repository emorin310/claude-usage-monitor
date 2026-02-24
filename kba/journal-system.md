# 📓 Journal System KBA

**Purpose:** Maintain a running log of all tasks, projects, events, and activities for daily/weekly review.

---

## Overview

The journal (`journal.md`) is Magi's activity log - a timestamped record of everything noteworthy that happens. It feeds into daily and weekly digests for Eric's review.

---

## File Location

```
~/clawd-magi/journal.md
```

---

## Entry Format

```markdown
### HH:MM - Title
- **Type:** Task | Project | Event | Activity | Routine | Alert
- **What:** One-line summary
- **Details:** Additional context (optional)
- **Link:** [Text](url) (optional)
```

### Entry Types

| Type | When to Use | Example |
|------|-------------|---------|
| **Task** | Single action item completed | "Set up log rotation" |
| **Project** | Multi-step initiative started/updated | "Gmail Inbox Competition launched" |
| **Event** | Calendar event or meeting | "Team standup at 10am" |
| **Activity** | General work performed | "Posted updates to Council" |
| **Routine** | Recurring scheduled task | "Morning briefing sent" |
| **Alert** | Important notification/warning | "Marvin gateway down" |

---

## Daily Structure

Each day gets its own section with the format:

```markdown
## YYYY-MM-DD (DayName)

### HH:MM - Entry Title
- **Type:** ...
```

Days are ordered newest-first. Entries within a day are also newest-first.

---

## When to Add Entries

Add journal entries for:

✅ **Always Log:**
- Tasks completed
- New projects started
- Significant decisions made
- Communications sent (Council posts, Telegram alerts)
- Errors or issues encountered
- Sub-agent work completed

⚠️ **Selectively Log:**
- Routine heartbeat checks (only if something notable)
- Minor file edits
- Internal processing

❌ **Don't Log:**
- Every heartbeat (too noisy)
- Failed/retried operations (unless significant)
- Internal tool calls

---

## Manual Entry (Script)

```bash
~/clawd-magi/scripts/journal-entry.sh "Type" "Title" "What" "Details" "Link"
```

**Example:**
```bash
./journal-entry.sh "Task" "Log rotation setup" "Created auto-archive for logs" "Daily at midnight, 30-day retention" ""
```

---

## Manual Entry (Direct Edit)

1. Open `~/clawd-magi/journal.md`
2. Find today's date section (or create if missing)
3. Add entry below the date header
4. Update "Last updated" timestamp at bottom

---

## Integration Points

### Daily Briefing (8am)
- Links to journal.md
- Shows count of today's entries
- Highlights key items

### Weekly Digest (Sunday 9am)
- Summarizes week's entries by type
- Counts: X Tasks, Y Projects, Z Events...
- Highlights accomplishments

### Heartbeat Checks
- HEARTBEAT.md includes "Journal Updates" section
- Add entries during heartbeats for significant activities

---

## Maintenance

### Daily (Automatic)
- New day section created as needed
- Entries added during normal operation

### Weekly (Manual/Review)
- Archive old entries (>30 days) if file gets large
- Review for patterns/insights

### Monthly
- Consider summarizing old months into `journal-archive-YYYY-MM.md`

---

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| `morning-briefing` | 8am daily | Includes journal link |
| `weekly-digest` | 9am Sunday | Summarizes week's entries |

---

## Quick Reference

**View Journal:**
```bash
cat ~/clawd-magi/journal.md
```

**Today's Entries:**
```bash
grep -A 50 "$(date +%Y-%m-%d)" ~/clawd-magi/journal.md
```

**Entry Count:**
```bash
grep -c "^### " ~/clawd-magi/journal.md
```

**Link for Telegram:**
```
file:///Users/eric/clawd-magi/journal.md
```

---

## Troubleshooting

### Missing Day Section
The script auto-creates day sections. If missing, add manually:
```markdown
## YYYY-MM-DD (DayName)
```

### Duplicate Entries
Check before adding - search for similar title in today's section.

### File Too Large (>100KB)
Archive older months:
```bash
grep -A 1000 "## 2026-01" journal.md > journal-archive-2026-01.md
# Then remove those sections from main journal
```

---

*Created: 2026-02-02*
*Author: Magi*
*Location: ~/clawd-magi/kba/journal-system.md*
