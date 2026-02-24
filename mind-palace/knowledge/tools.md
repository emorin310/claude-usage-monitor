# Tools & Integrations

## Messaging

### Telegram
- **Eric's Chat ID:** 6643669380
- **Use for:** Appointment notifications, alerts, proactive messages

### BlueBubbles (iMessage)
- **Use for:** Listening to family chats, appointment detection
- **Rule:** Silent by default, respond only on @magi

## Task Management

### Todoist
- **API Token:** `1425e4eff8e83fc361d6bdd4ac9922c34d5089db`
- **Base URL:** `https://api.todoist.com/rest/v2`
- **Docs:** https://developer.todoist.com/rest/v2

#### Common Endpoints
```bash
# List tasks
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.todoist.com/rest/v2/tasks"

# Filter by label
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.todoist.com/rest/v2/tasks?filter=%40magi"

# Get comments
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.todoist.com/rest/v2/comments?task_id=TASK_ID"

# Complete task
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  "https://api.todoist.com/rest/v2/tasks/TASK_ID/close"
```

#### Key Project IDs
- AI Council: `2366297739`

#### Key Task IDs (Council Board)
- Announcements: `9960450380`
- Handoffs: `9960450396`
- Status Updates: `9960450404`
- Questions for Eric: `9960450417`

#### Mobile Deep Links (iPhone)
When sending tasks to Eric via Telegram, use **web URLs** with v2_id format:
```
https://app.todoist.com/app/task/[v2_id]
```

**Important:** REST API returns old numeric IDs. Must use **Sync API** to get `v2_id`:
```bash
curl -X POST "https://api.todoist.com/sync/v9/sync" \
  -H "Authorization: Bearer $token" \
  -d "sync_token=*" \
  -d "resource_types=[\"items\"]"
```
Response includes both `id` (numeric) and `v2_id` (alphanumeric for URLs).

**Telegram formatting:** Use markdown links for clean embedded text:
```
[Task Name](https://app.todoist.com/app/task/v2_id)
```
- ✅ Markdown `[text](url)` works
- ❌ HTML `<a href="">` shows raw tags
- ❌ Custom schemes `todoist://` don't auto-link

## Calendar

### gcalcli
- **Personal calendar:** `emorin310@gmail.com`
- **Family calendar:** `Family`

#### Add Event
```bash
gcalcli add --calendar "emorin310@gmail.com" \
  --title "Event Name" \
  --where "Location" \
  --when "Jan 31, 2026 11:30 AM" \
  --duration 60 \
  --noprompt
```

#### Appointment Flow
1. Detect in iMessage/Gmail
2. Parse: title, date, time, location
3. Notify Eric via Telegram
4. On approval: Add to BOTH calendars (personal + Family with "- Eric" suffix)

## Email

### Gmail
- Script: `~/clawd-magi/scripts/gmail-check.py`
- Cron: Runs at :15 and :45 past each hour
- Detects: Appointment confirmations, reminders

## Monitoring

### Claude Usage
- Script: `~/clawd-magi/scripts/check-claude-usage.sh`
- Reads from Claude Usage Tool menu bar (AppleScript)
- Cron: Every 30 min
- Threshold: Alert at 75% for Opus→Sonnet consideration

## Web Search

### Brave Search
- Rate limit: 1 req/sec, 2000/month on free tier
- Use `web_search` tool
- Fallback: `web_fetch` for direct page content

---

*Last updated: 2026-01-29*
