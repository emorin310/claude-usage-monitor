#!/bin/bash
# Todoist No-Section Triage Script
# Scans inbox tasks without sections and suggests categorization

API_TOKEN="1425e4eff8e83fc361d6bdd4ac9922c34d5089db"
API_URL="https://api.todoist.com/api/v1/sync"

# Fetch all items
RESPONSE=$(curl -s "$API_URL" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d 'sync_token=*' \
  -d 'resource_types=["items","sections","projects"]')

# Get inbox project ID
INBOX_ID=$(echo "$RESPONSE" | jq -r '.projects[] | select(.name == "Inbox") | .id')

# Get tasks in inbox with no section
NO_SECTION_TASKS=$(echo "$RESPONSE" | jq -r --arg inbox "$INBOX_ID" '
  .items 
  | map(select(.project_id == $inbox and .section_id == null and .checked == false))
  | .[] 
  | {
      id: .id,
      content: .content,
      priority: .priority,
      labels: .labels,
      due: (.due.date // "no due date")
    }
')

# Count
COUNT=$(echo "$NO_SECTION_TASKS" | jq -s 'length')

# Get available sections in Inbox
SECTIONS=$(echo "$RESPONSE" | jq -r --arg inbox "$INBOX_ID" '
  .sections 
  | map(select(.project_id == $inbox)) 
  | .[] 
  | {id: .id, name: .name}
')

# Output report
cat << EOF
{
  "inbox_id": "$INBOX_ID",
  "no_section_count": $COUNT,
  "tasks": $(echo "$NO_SECTION_TASKS" | jq -s '.'),
  "available_sections": $(echo "$SECTIONS" | jq -s '.')
}
EOF
