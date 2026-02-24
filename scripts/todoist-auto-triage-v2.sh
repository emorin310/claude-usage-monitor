#!/bin/bash
# Auto-triage using Sync API v1

API_TOKEN="1425e4eff8e83fc361d6bdd4ac9922c34d5089db"
API_URL="https://api.todoist.com/api/v1/sync"

# Fetch all data
RESPONSE=$(curl -s "$API_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "sync_token=*" \
  -d "resource_types=[\"items\",\"sections\",\"projects\"]" \
  -d "token=$API_TOKEN")

# Get inbox project
INBOX_ID=$(echo "$RESPONSE" | jq -r '.projects[] | select(.name == "Inbox") | .id')

# Get sections
IC_TODO=$(echo "$RESPONSE" | jq -r --arg inbox "$INBOX_ID" '.sections[] | select(.project_id == $inbox and .name == "IC Todo List 🥕🔥") | .id')
IC_BACK=$(echo "$RESPONSE" | jq -r --arg inbox "$INBOX_ID" '.sections[] | select(.project_id == $inbox and (.name | contains("IC Backburner"))) | .id')
IC_REVIEW=$(echo "$RESPONSE" | jq -r --arg inbox "$INBOX_ID" '.sections[] | select(.project_id == $inbox and (.name | contains("IC under Review"))) | .id')
ERIC_FOCUS=$(echo "$RESPONSE" | jq -r --arg inbox "$INBOX_ID" '.sections[] | select(.project_id == $inbox and (.name | contains("Eric Focus"))) | .id')
PERSONAL=$(echo "$RESPONSE" | jq -r --arg inbox "$INBOX_ID" '.sections[] | select(.project_id == $inbox and (.name | contains("Personal Todo"))) | .id')
PERSONAL_BACK=$(echo "$RESPONSE" | jq -r --arg inbox "$INBOX_ID" '.sections[] | select(.project_id == $inbox and (.name | contains("Personal Backburner"))) | .id')

echo "📋 Todoist Auto-Triage Report (Sync API v1)"
echo "=============================="
echo ""

# Get unsectioned tasks
echo "$RESPONSE" | jq -r --arg inbox "$INBOX_ID" '
  .items[] 
  | select(.project_id == $inbox and .section_id == null and .is_deleted == 0 and .checked == 0)
  | {
      id: .id,
      content: .content,
      labels: .labels,
      priority: .priority,
      due: (.due.date // "none")
    }
' | jq -c '.' | head -30 | while IFS= read -r task; do
  CONTENT=$(echo "$task" | jq -r '.content')
  LABELS=$(echo "$task" | jq -r '.labels | join(", ")')
  PRIORITY=$(echo "$task" | jq -r '.priority')
  
  TARGET=""
  REASON=""
  
  # Categorization logic
  if echo "$LABELS" | grep -qi "instacart"; then
    if [ "$PRIORITY" -ge "3" ]; then
      TARGET="IC Todo ($IC_TODO)"
      REASON="Instacart + priority $PRIORITY"
    else
      TARGET="IC Backburner ($IC_BACK)"
      REASON="Instacart low-pri"
    fi
  elif echo "$LABELS" | grep -qi "magi"; then
    TARGET="Personal ($PERSONAL)"
    REASON="Magi label"
  elif echo "$CONTENT" | grep -qi "champ\|peer review\|manager"; then
    TARGET="IC Todo ($IC_TODO)"
    REASON="Work keywords"
  elif echo "$CONTENT" | grep -qi "claude\|AI\|bot\|magi"; then
    TARGET="Personal ($PERSONAL)"
    REASON="AI/bot task"
  elif echo "$CONTENT" | grep -qi "battery\|UPS\|infrastructure"; then
    TARGET="Personal ($PERSONAL)"
    REASON="Tech/infra"
  fi
  
  if [ -n "$TARGET" ]; then
    echo "✓ $CONTENT → $REASON"
  else
    echo "? $CONTENT → Uncategorized"
  fi
done

echo ""
echo "=============================="
echo "✅ Dry run complete. Review suggestions above."
echo ""
echo "Next steps:"
echo "  1. Approve these rules"
echo "  2. I'll add the move logic"
echo "  3. Set up daily cron job"
