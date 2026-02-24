# HEARTBEAT.md

**⚠️ MODEL REQUIREMENT: All heartbeat checks MUST use haiku (cost optimization)**

## Quick Checks (rotate through these)

### Council Comms (Priority)
- Check comment counts on Council threads (IDs: 9960450380, 9960450396, 9960450404, 9960450417)
- If new comments detected, read and respond if needed (max 1 response per heartbeat)
- Update memory/council-state.json if changes found

### Daily Items
- Check for overdue tasks in Todoist (@magi label)
- Check for `needs-magi` labeled tasks → Eric wants my attention on these
- Check "👀 Needs Eric" section for pending items

### Journal Updates
- Add entries to journal.md for significant activities
- Types: Task, Project, Event, Activity, Routine, Alert
- Keep entries concise (1-2 lines)
- Include links where relevant

## Notes
- Don't spam the council board - max 1 comment per heartbeat if truly needed
- Council-monitor cron handles deep checks at 10am and 6pm
- Journal entries should capture anything noteworthy
- If urgent, notify Eric via Telegram
