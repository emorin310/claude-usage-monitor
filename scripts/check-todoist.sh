#!/bin/bash
# Todoist API v1 Sync monitoring script
# Uses the Sync API (/api/v1/sync) instead of deprecated REST v2

API_TOKEN=$(cat ~/.config/todoist/api-token)
API_URL="https://api.todoist.com/api/v1/sync"

# Council Comms thread IDs (Sync API uses different IDs than REST API)
ANNOUNCEMENTS="6frPQG28vCpmHfPQ"
HANDOFFS="6frPQFwgCmJgGvjQ"
STATUS_UPDATES="6frPQG5Crjcqx55Q"
QUESTIONS="6frPQG8RFCMXpQhx"

# Fetch all items and notes in one call
RESPONSE=$(curl -s "$API_URL" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d 'sync_token=*' \
  -d 'resource_types=["items","notes","labels"]')

# Count comments on each Council thread
count_announcements=$(echo "$RESPONSE" | jq -r ".notes | map(select(.item_id == \"$ANNOUNCEMENTS\")) | length")
count_handoffs=$(echo "$RESPONSE" | jq -r ".notes | map(select(.item_id == \"$HANDOFFS\")) | length")
count_status=$(echo "$RESPONSE" | jq -r ".notes | map(select(.item_id == \"$STATUS_UPDATES\")) | length")
count_questions=$(echo "$RESPONSE" | jq -r ".notes | map(select(.item_id == \"$QUESTIONS\")) | length")

# Get all tasks with @magi label (labels are stored as name strings in Sync API)
magi_tasks=$(echo "$RESPONSE" | jq -r '.items | map(select((.labels | contains(["magi"])) and .checked == false)) | length')

# Get overdue @magi tasks (tasks with due date in the past)
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
overdue_tasks=$(echo "$RESPONSE" | jq -r --arg now "$NOW" '
  .items 
  | map(select((.labels | contains(["magi"])) and .due != null and .due.date < $now and .checked == false)) 
  | length
')

# Get needs-magi tasks
needs_magi_tasks=$(echo "$RESPONSE" | jq -r '.items | map(select((.labels | contains(["needs-magi"])) and .checked == false)) | length')

# Output JSON
cat << EOF
{
  "council_threads": {
    "announcements": $count_announcements,
    "handoffs": $count_handoffs,
    "status_updates": $count_status,
    "questions": $count_questions
  },
  "tasks": {
    "total_magi": $magi_tasks,
    "overdue": $overdue_tasks,
    "needs_magi": $needs_magi_tasks
  },
  "checked_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
