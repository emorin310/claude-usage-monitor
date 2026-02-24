#!/usr/bin/env bash
# magi-marvin-chat.sh - Direct messaging protocol via Todoist message bus
# Usage: ./magi-marvin-chat.sh "Your message"

set -euo pipefail

TODOIST_TOKEN="1425e4eff8e83fc361d6bdd4ac9922c34d5089db"
HANDOFFS_TASK_ID="9960450396"  # Council Handoffs thread
LOG_FILE="$HOME/clawd-magi/marvin.md.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
MODEL="${2:-ollama/llama3.1:8b}"

if [ $# -eq 0 ]; then
  echo "Usage: $0 \"message\" [model]"
  exit 1
fi

MESSAGE="$1"

# Log outgoing
echo "[$TIMESTAMP] [MAGI → MARVIN] $MESSAGE" >> "$LOG_FILE"

# Send via Todoist comment with special marker
COMMENT=$(cat <<EOF
🤖💬 **[DIRECT_MSG from Magi using $MODEL]**

$MESSAGE

---
*Reply using deepseek-r1 model*
EOF
)

# Post to Todoist
RESPONSE=$(curl -s -X POST "https://api.todoist.com/api/v1/comments" \
  -H "Authorization: Bearer $TODOIST_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"task_id\": \"$HANDOFFS_TASK_ID\", \"content\": $(echo "$COMMENT" | jq -Rs .)}")

COMMENT_ID=$(echo "$RESPONSE" | jq -r '.id')

if [ "$COMMENT_ID" != "null" ]; then
  echo "✅ Message sent to Marvin (Comment ID: $COMMENT_ID)"
  echo "[$TIMESTAMP] [SYSTEM] Message sent via Todoist (ID: $COMMENT_ID)" >> "$LOG_FILE"
else
  echo "❌ Failed to send message"
  echo "Response: $RESPONSE"
fi
