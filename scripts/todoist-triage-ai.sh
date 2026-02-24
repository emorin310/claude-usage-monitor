#!/bin/bash
# AI-powered Todoist Triage
# Categorizes "No Section" tasks and generates report

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRIAGE_DATA=$("$SCRIPT_DIR/todoist-triage.sh")

# Save raw data for AI analysis
TRIAGE_FILE="/tmp/todoist-triage-$(date +%Y%m%d).json"
echo "$TRIAGE_DATA" > "$TRIAGE_FILE"

COUNT=$(echo "$TRIAGE_DATA" | jq -r '.no_section_count')

if [ "$COUNT" -eq 0 ]; then
  echo "✅ Inbox is clean! No tasks without sections."
  exit 0
fi

echo "📋 Found $COUNT tasks without sections"
echo ""
echo "Analyzing with AI..."
echo ""

# Call OpenClaw to analyze and suggest categorization
openclaw chat --agent main --message "
I have $COUNT Todoist tasks in my Inbox with no section assigned.

**Available sections:**
- 🎯 Eric Focus (ID: 6frV5Xp7jqr2VWx6) - High-priority personal focus items
- IC Todo List 🥕🔥 (ID: 6cF9Q8QmJqM2MFr6) - Instacart work tasks  
- IC Backburner 🥕 (ID: 6cF9QCMMvGGCg6Cc) - Instacart low-priority
- IC under Review (ID: 6ch47CwjGqfXfm46) - Instacart items awaiting review
- Personal Todo List ✅ (ID: 6cF9QGjxW66mfW66) - Personal tasks
- Personal Backburner (ID: 6frVjj98wfrxQM5c) - Personal low-priority

**Task data:** $(cat $TRIAGE_FILE)

Please analyze the first 20 tasks and suggest which section each should go to. Format your response as:

\`\`\`json
{
  \"suggestions\": [
    {\"task_id\": \"...\", \"task_name\": \"...\", \"suggested_section_id\": \"...\", \"section_name\": \"...\", \"reason\": \"...\"},
    ...
  ]
}
\`\`\`

Focus on tasks with labels (magi, instacart, etc.) or clear context clues.
"

echo ""
echo "✅ Triage analysis complete!"
echo "Review the suggestions above and let me know if you want me to:"
echo "  1. Auto-apply these changes"
echo "  2. Generate a daily report"
echo "  3. Adjust the categorization logic"
