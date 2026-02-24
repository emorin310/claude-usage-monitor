# Cron Reference

## Active Cron Jobs

### Gmail Appointment Checker

**Script:** `~/clawd-magi/scripts/gmail-check.py (DISABLED)`
**Schedule:** `:15` and `:45` past each hour (2x/hour)
**Purpose:** Detect appointment confirmations in Gmail

```cron
15,45 * * * * /usr/bin/python3 ~/clawd-magi/scripts/gmail-check.py (DISABLED)
```

**What it does:**
1. Scans last 3 days of emails
2. Searches for appointment keywords (confirmed, scheduled, reminder)
3. Looks for medical provider mentions (dentist, chiro, doctor)
4. Outputs JSON with found appointments

**Dependencies:**
- `~/.clawdbot/credentials/gmail_token.pickle`
- `~/.clawdbot/credentials/gmail_client_secrets.json`
- Google Gmail API OAuth credentials

**Related runbook:** `runbooks/appointment-flow.md`

---

### Claude Usage Monitor

**Script:** `~/clawd-magi/scripts/check-claude-usage.sh`
**Schedule:** Every 30 minutes
**Purpose:** Track Claude API usage to manage costs

```cron
*/30 * * * * ~/clawd-magi/scripts/check-claude-usage.sh
```

**What it does:**
1. Uses AppleScript to read Claude Usage Tool menu bar app
2. Extracts: all_models, sonnet_only, current_session, extra_usage
3. Outputs JSON

**Output format:**
```json
{"all_models": 45, "sonnet_only": 20, "current_session": 5, "extra_usage": 0}
```

**Threshold:** Alert at 75% for Opus→Sonnet consideration

---

### Auto Model Switch

**Script:** `~/clawd-magi/scripts/auto-model-switch.sh`
**Schedule:** Triggered by usage monitor (not standalone cron)
**Purpose:** Automatically switch to cheaper model when usage high

**What it does:**
- Checks usage thresholds
- Suggests or auto-switches to Sonnet when Opus quota depleted

---

### Todoist Monitor

**Script:** Built into Clawdbot/heartbeat system
**Schedule:** Via heartbeat (2-4x daily)
**Purpose:** Check for tasks needing attention

**What it checks:**
- Tasks with `@magi` label
- Tasks with `needs-magi` label
- Council board comments (task IDs in `knowledge/tools.md`)
- Overdue tasks

---

## Clawdbot Scheduled Tasks

These run via Clawdbot's internal scheduler, not system cron:

| Time | Task | Type |
|------|------|------|
| 7:00 AM | Morning briefing research | Scheduled |
| 8:00 AM | Morning briefing delivery | Scheduled |
| 9:00 AM | Scavenger hunt | Scheduled |
| 12:00 PM | Workflow optimization | Scheduled |
| Variable | Heartbeat checks | Polling (2-4x/day) |

---

## Adding New Cron Jobs

1. Create script in `~/clawd-magi/scripts/`
2. Make executable: `chmod +x script.sh`
3. Add to crontab: `crontab -e`
4. Document here with schedule, purpose, dependencies

**Cron format reminder:**
```
* * * * * command
│ │ │ │ │
│ │ │ │ └── Day of week (0-7, 0=Sunday)
│ │ │ └──── Month (1-12)
│ │ └────── Day of month (1-31)
│ └──────── Hour (0-23)
└────────── Minute (0-59)
```

---

*Last updated: 2026-01-29*
