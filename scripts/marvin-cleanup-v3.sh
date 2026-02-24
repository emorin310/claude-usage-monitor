#!/bin/bash
# Marvin Cleanup Script v3
# Fixed: timezone handling, duplicate prevention, better error handling

set -e

echo "🔧 Marvin Cleanup v3"
echo "==================="
echo ""

cd ~/clawdbot

# Backup everything first
echo "1. Creating backups..."
cp ~/.clawdbot/cron/jobs.json ~/.clawdbot/cron/jobs.json.backup-$(date +%Y%m%d-%H%M%S)
cp ~/.clawdbot/agents/main/sessions/sessions.json ~/.clawdbot/agents/main/sessions/sessions.json.backup-$(date +%Y%m%d-%H%M%S)
echo "   ✅ Backups created"

# Step 1: Delete ALL old crons (both main duplicates and old ones)
echo ""
echo "2. Removing old crons..."

# Get list of old cron IDs to remove
OLD_MAIN_CRONS=$(jq -r '.jobs[] | select(.agentId == "main") | .id' ~/.clawdbot/cron/jobs.json)

# Remove them from the file
jq 'del(.jobs[] | select(.agentId == "main"))' ~/.clawdbot/cron/jobs.json > ~/.clawdbot/cron/jobs.json.tmp
mv ~/.clawdbot/cron/jobs.json.tmp ~/.clawdbot/cron/jobs.json

OLD_COUNT=$(echo "$OLD_MAIN_CRONS" | wc -l)
echo "   ✅ Removed $OLD_COUNT old main-agent crons"

# Step 2: Create worker agent if needed
echo ""
echo "3. Checking worker agent..."
if [ -d ~/.clawdbot/agents/worker ]; then
  echo "   ✅ Worker agent exists"
else
  echo "   Creating worker agent..."
  timeout 60 npx clawdbot agents add worker \
    --workspace ~/clawdbot-worker \
    --model "deepseek/deepseek-reasoner" \
    --non-interactive \
    --json || echo "   ⚠️  Timeout, but may have succeeded"
fi

# Step 3: Set up minimal workspace
echo ""
echo "4. Setting up worker workspace..."
mkdir -p ~/clawdbot-worker

cat > ~/clawdbot-worker/SOUL.md << 'EOF'
# Worker Bot
Execute tasks efficiently. Stay silent unless reporting results or errors.
EOF

cat > ~/clawdbot-worker/USER.md << 'EOF'
# User: Eric Morin
- Timezone: EST (America/Toronto)
- Telegram: 6643669380
EOF

cat > ~/clawdbot-worker/AGENTS.md << 'EOF'
# Worker Agent
Execute assigned tasks. Report results.
EOF

echo "   ✅ Workspace ready"

# Step 4: Create new crons for remaining jobs
echo ""
echo "5. Creating new crons on worker agent..."

# Define all crons explicitly with proper schedules
declare -A CRONS
CRONS["kanban-watch"]="*/5 * * * *|Check Kanban board for updates"
CRONS["ups-battery"]="0 */6 * * *|Monitor UPS battery status"
CRONS["docker-health"]="*/15 * * * *|Check Docker container health"
CRONS["kanban-todoist-sync"]="0 * * * *|Sync Kanban with Todoist"
CRONS["claude-credit"]="0 0 * * *|Monitor Claude API credits"
CRONS["security-audit"]="0 2 * * 0|Weekly security audit"
CRONS["council-checkin"]="0 9 * * *|Daily Todoist Council check-in"

for cron_name in "${!CRONS[@]}"; do
  IFS='|' read -r schedule message <<< "${CRONS[$cron_name]}"
  echo "   Creating: $cron_name"
  
  timeout 30 npx clawdbot cron add \
    --name "$cron_name" \
    --cron "$schedule" \
    --tz "America/Toronto" \
    --session isolated \
    --agent worker \
    --message "$message" \
    --model "deepseek/deepseek-reasoner" 2>&1 | head -3 || echo "   ⚠️  May have timed out"
done

echo "   ✅ New crons created"

# Step 5: Clean duplicate worker crons (keep only latest)
echo ""
echo "6. Cleaning duplicate worker crons..."

# Get duplicates and keep only the newest ID for each name
jq '
  .jobs |= (
    group_by(.name) |
    map(
      if length > 1 then
        sort_by(.createdAtMs) | .[length-1:]
      else
        .
      end
    ) |
    flatten
  )
' ~/.clawdbot/cron/jobs.json > ~/.clawdbot/cron/jobs.json.deduped
mv ~/.clawdbot/cron/jobs.json.deduped ~/.clawdbot/cron/jobs.json

echo "   ✅ Duplicates removed"

# Step 6: Clean sessions
echo ""
echo "7. Cleaning sessions..."

# Remove zombie sessions and old cron sessions
cd ~/.clawdbot/agents/main/sessions
jq '
  with_entries(
    select(
      .key == "agent:main:main" or
      (.key | test("^agent:main:discord:"))
    )
  )
' sessions.json > sessions.json.clean
mv sessions.json.clean sessions.json

# Clean worker sessions
if [ -d ~/.clawdbot/agents/worker/sessions ]; then
  rm -f ~/.clawdbot/agents/worker/sessions/*.jsonl
  echo '{}' > ~/.clawdbot/agents/worker/sessions/sessions.json
fi

echo "   ✅ Sessions cleaned"

# Final report
echo ""
echo "=" 
echo "✅ Cleanup Complete!"
echo "="
echo ""

# Count final state
TOTAL_CRONS=$(jq '.jobs | length' ~/.clawdbot/cron/jobs.json)
WORKER_CRONS=$(jq '[.jobs[] | select(.agentId == "worker")] | length' ~/.clawdbot/cron/jobs.json)
MAIN_CRONS=$(jq '[.jobs[] | select(.agentId == "main")] | length' ~/.clawdbot/cron/jobs.json)
MAIN_SESSIONS=$(jq 'keys | length' ~/.clawdbot/agents/main/sessions/sessions.json)

echo "Final state:"
echo "  Total crons: $TOTAL_CRONS"
echo "  Worker crons: $WORKER_CRONS"
echo "  Main crons: $MAIN_CRONS"
echo "  Main sessions: $MAIN_SESSIONS"
echo ""

if [ "$MAIN_CRONS" -gt 0 ]; then
  echo "⚠️  Warning: $MAIN_CRONS crons still on main agent!"
  jq -r '[.jobs[] | select(.agentId == "main") | .name] | .[]' ~/.clawdbot/cron/jobs.json
fi

echo ""
echo "Backups saved in ~/.clawdbot/cron/ and ~/.clawdbot/agents/main/sessions/"
echo ""
echo "Verify with: npx clawdbot cron list"
