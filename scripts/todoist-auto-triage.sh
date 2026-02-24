#!/bin/bash
# Auto-triage Todoist inbox tasks based on labels and keywords

API_TOKEN="1425e4eff8e83fc361d6bdd4ac9922c34d5089db"
API_URL="https://api.todoist.com/rest/v2"

# Section mappings
SECTION_IC_TODO="6cF9Q8QmJqM2MFr6"      # IC Todo List
SECTION_IC_BACKBURNER="6cF9QCMMvGGCg6Cc" # IC Backburner
SECTION_IC_REVIEW="6ch47CwjGqfXfm46"     # IC under Review
SECTION_ERIC_FOCUS="6frV5Xp7jqr2VWx6"    # Eric Focus
SECTION_PERSONAL="6cF9QGjxW66mfW66"      # Personal Todo List
SECTION_PERSONAL_BACK="6frVjj98wfrxQM5c" # Personal Backburner

# Get inbox project ID
INBOX_ID=$(curl -s "$API_URL/projects" -H "Authorization: Bearer $API_TOKEN" | jq -r '.[] | select(.name == "Inbox") | .id')

# Get all inbox tasks without sections
TASKS=$(curl -s "$API_URL/tasks?project_id=$INBOX_ID" -H "Authorization: Bearer $API_TOKEN" | jq -r '.[] | select(.section_id == null)')

echo "📋 Todoist Auto-Triage Report"
echo "=============================="
echo ""

MOVED=0
TOTAL=$(echo "$TASKS" | jq -s 'length')

echo "Found $TOTAL tasks without sections"
echo ""

# Process each task
echo "$TASKS" | jq -c '.' | while IFS= read -r task; do
  TASK_ID=$(echo "$task" | jq -r '.id')
  TASK_CONTENT=$(echo "$task" | jq -r '.content')
  TASK_LABELS=$(echo "$task" | jq -r '.labels | join(", ")')
  TASK_PRIORITY=$(echo "$task" | jq -r '.priority')
  
  TARGET_SECTION=""
  REASON=""
  
  # Rule 1: Check labels
  if echo "$TASK_LABELS" | grep -qi "instacart\|🥕"; then
    if echo "$TASK_PRIORITY" | grep -q "4"; then
      TARGET_SECTION="$SECTION_IC_TODO"
      REASON="Instacart + high priority"
    else
      TARGET_SECTION="$SECTION_IC_BACKBURNER"
      REASON="Instacart label"
    fi
  elif echo "$TASK_LABELS" | grep -qi "magi"; then
    TARGET_SECTION="$SECTION_PERSONAL"
    REASON="Magi label"
  elif echo "$TASK_LABELS" | grep -qi "needs-eric\|eric"; then
    TARGET_SECTION="$SECTION_ERIC_FOCUS"
    REASON="Needs Eric's attention"
  
  # Rule 2: Check keywords in content
  elif echo "$TASK_CONTENT" | grep -qi "champ\|peer review\|manager\|M1\|work"; then
    TARGET_SECTION="$SECTION_IC_TODO"
    REASON="Work-related keywords"
  elif echo "$TASK_CONTENT" | grep -qi "claude\|magi\|marvin\|AI\|bot"; then
    TARGET_SECTION="$SECTION_PERSONAL"
    REASON="AI/bot keywords"
  elif echo "$TASK_CONTENT" | grep -qi "battery\|UPS\|infrastructure\|backup"; then
    TARGET_SECTION="$SECTION_PERSONAL"
    REASON="Tech/infrastructure"
  fi
  
  # Rule 3: Priority override
  if [ "$TASK_PRIORITY" = "4" ] && [ -n "$TARGET_SECTION" ]; then
    if [ "$TARGET_SECTION" = "$SECTION_PERSONAL" ]; then
      TARGET_SECTION="$SECTION_ERIC_FOCUS"
      REASON="$REASON + P1 priority"
    fi
  fi
  
  if [ -n "$TARGET_SECTION" ]; then
    echo "✓ \"$TASK_CONTENT\" → $REASON"
    # Uncomment to actually move:
    # curl -s -X POST "$API_URL/tasks/$TASK_ID" \
    #   -H "Authorization: Bearer $API_TOKEN" \
    #   -H "Content-Type: application/json" \
    #   -d "{\"section_id\": \"$TARGET_SECTION\"}" > /dev/null
    MOVED=$((MOVED + 1))
  else
    echo "? \"$TASK_CONTENT\" → No clear category"
  fi
done

echo ""
echo "=============================="
echo "Would categorize: $MOVED tasks"
echo "Remaining unsorted: $((TOTAL - MOVED)) tasks"
echo ""
echo "To enable auto-move, uncomment the curl line in the script."
