# HEARTBEAT.md

**⚠️ MODEL REQUIREMENT: All heartbeat checks MUST use haiku (cost optimization)**

## 🔄 Coordinated Health Monitoring

**NEW:** We now have comprehensive health monitoring via cron jobs (every 30 min) + heartbeats. Avoid duplication!

### Heartbeat Role (Manual Checks)
- **Todoist Council Comms** - Check for new comments, respond if needed
- **System alerts review** - Check `/tmp/health_check_final_results.json` for any pending alerts
- **Memory maintenance** - Update journal.md, review MEMORY.md
- **Ad-hoc tasks** - Anything Eric specifically requests

### Cron Job Role (Automated Checks)  
- **Gmail monitoring** - Urgent emails, security alerts, payment failures (DRAFT-ONLY)
- **Calendar alerts** - Events in next 2 hours
- **System health** - Disk space, memory usage, service status
- **Auto-maintenance** - Updates (4 AM), backups (4:30 AM)

## Quick Checks (Priority Order)

### 1. Council Comms & Tasks 
- Run `/home/magi/clawd/scripts/check-todoist.sh` to get current state
- Compare with memory/council-state.json to detect changes
- If new comments on Council threads, read and respond if needed (max 1 response per heartbeat)
- If overdue tasks > 0, flag for attention
- If needs-magi tasks > 0, review and act on them
- Update memory/council-state.json if changes found

### 2. Health Alerts Review
- Check `/tmp/health_check_final_results.json` if it exists
- Review any "alert" or "error" status items from cron health checks
- Escalate to Eric if manual intervention needed
- Clear processed alerts

### 3. Memory & Journal Updates
- Add entries to journal.md for significant activities
- Types: Task, Project, Event, Activity, Routine, Alert
- Keep entries concise (1-2 lines)
- Include links where relevant
- Periodically review and update MEMORY.md with distilled learnings

### 4. Proactive Opportunities (Time Permitting)
- Organize workspace files
- Review and update documentation
- Check for stuck processes or background tasks
- Commit and push workspace changes

## Coordination Rules
- **No duplicate notifications** - If cron already sent an alert, don't repeat it
- **Escalation only** - Heartbeat handles what cron can't (complex reasoning, context)  
- **Max 1 response per heartbeat** to council threads (avoid spam)
- **Urgent path** - Serious issues go directly to Eric via Discord
- **Use state files** - Track what's been checked to avoid redundancy

## Notes
- Cron handles routine monitoring; heartbeat handles reasoning and complex responses
- If cron jobs fail, heartbeat can serve as backup
- All health monitoring results logged to `/home/magi/clawd/logs/`
