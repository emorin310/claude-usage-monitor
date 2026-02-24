# Runbook: Heartbeat Protocol

## What Is a Heartbeat?

Periodic check-in from cron system. Prompt:
> "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."

## Response Rules

- **Nothing needs attention:** Reply exactly `HEARTBEAT_OK`
- **Something needs attention:** Take action, DO NOT include HEARTBEAT_OK
- **Don't infer:** Only act on explicit checklist items
- **Don't repeat:** Check if task was already done this cycle

## Standard Checklist (from HEARTBEAT.md)

### Priority: Council Comms
- Check comment counts on council threads
- IDs: 9960450380, 9960450396, 9960450404, 9960450417
- If new comments: read and respond if needed (max 1 response per heartbeat)
- Update state/council-state.json if changes

### Daily Items
- Check for overdue tasks in Todoist (@magi label)
- Check for `needs-magi` labeled tasks
- Check "👀 Needs Eric" section for pending items

## Fetch Council Comments

```bash
token="YOUR_TOKEN"
curl -s -H "Authorization: Bearer $token" \
  "https://api.todoist.com/rest/v2/comments?task_id=9960450380"
```

## When to Be Proactive (Not Just Ack)

- Important email arrived
- Calendar event coming up (<2h)
- Something interesting found
- >8h since last contact with Eric
- Overdue high-priority task

## When to Stay Quiet (HEARTBEAT_OK)

- Late night (23:00-08:00) unless urgent
- Eric is clearly busy
- Nothing new since last check
- Just checked <30 minutes ago

## Background Work (No Permission Needed)

- Read and organize memory files
- Check on projects (git status)
- Update documentation
- Commit and push own changes
- Review and update MEMORY.md

---

*Last updated: 2026-01-29*
