#!/bin/bash
# Marvin Model Migration Script v2
# Migrates cron jobs from main agent to worker agent with DeepSeek
# Includes zombie session cleanup

set -e

echo "🔧 Marvin Model Migration v2"
echo "============================"
echo ""

cd ~/clawdbot

# 1. Create worker agent
echo "1. Creating worker agent..."
npx clawdbot agents add worker \
  --workspace ~/clawdbot-worker \
  --model "deepseek/deepseek-reasoner" \
  --non-interactive \
  --json || echo "Worker agent may already exist"

# 2. Set up minimal worker workspace
echo "2. Setting up minimal workspace..."
mkdir -p ~/clawdbot-worker

cat > ~/clawdbot-worker/SOUL.md << 'EOF'
# Worker Bot

Execute tasks efficiently. No personality needed. Stay silent unless reporting results or errors.
EOF

cat > ~/clawdbot-worker/USER.md << 'EOF'
# User: Eric Morin
- Timezone: EST (America/Toronto)
- Discord: emorin310 (793158038881042434)
EOF

cat > ~/clawdbot-worker/AGENTS.md << 'EOF'
# Worker Agent

Execute assigned tasks. Report results. Stay silent on success unless output is expected.
EOF

# 3. Get list of current cron jobs directly from file
echo "3. Reading current cron jobs..."
if [ -f ~/.clawdbot/cron/jobs.json ]; then
  cp ~/.clawdbot/cron/jobs.json /tmp/marvin-crons-backup.json
  echo "   Backup saved to /tmp/marvin-crons-backup.json"
else
  echo "   ERROR: cron jobs file not found!"
  exit 1
fi

# 4. Extract cron details and recreate
echo "4. Migrating cron jobs to worker agent..."
jq -r '.jobs[] | "\(.id)|\(.name)|\(.schedule.expr)|\(.schedule.tz)|\(.payload.message)"' ~/.clawdbot/cron/jobs.json | while IFS='|' read -r id name schedule tz message; do
  echo "  - Processing: $name"
  
  # Remove old cron (via file edit since npx hangs)
  jq --arg id "$id" 'del(.jobs[] | select(.id == $id))' ~/.clawdbot/cron/jobs.json > ~/.clawdbot/cron/jobs.json.tmp
  mv ~/.clawdbot/cron/jobs.json.tmp ~/.clawdbot/cron/jobs.json
  
  # Create new cron with worker agent
  npx clawdbot cron add \
    --name "$name" \
    --cron "$schedule" \
    --tz "${tz:-America/Toronto}" \
    --session isolated \
    --agent worker \
    --message "$message" \
    --model "deepseek/deepseek-reasoner" 2>&1 | head -3
done

# 5. Clean zombie sessions
echo "5. Cleaning sessions..."

# Identify zombie session IDs (sessions not matching any current cron)
ACTIVE_CRON_IDS=$(jq -r '.jobs[].id' ~/.clawdbot/cron/jobs.json | tr '\n' '|' | sed 's/|$//')

# Keep only main session and sessions matching active crons
cd ~/.clawdbot/agents/main/sessions
jq --arg pattern "agent:main:cron:($ACTIVE_CRON_IDS)" '
  with_entries(
    select(
      .key == "agent:main:main" or 
      (.key | test($pattern))
    )
  )
' sessions.json > sessions.json.new

mv sessions.json.new sessions.json

# 6. Clean worker sessions (fresh start)
if [ -d ~/.clawdbot/agents/worker/sessions ]; then
  rm -f ~/.clawdbot/agents/worker/sessions/*.jsonl
  echo '{}' > ~/.clawdbot/agents/worker/sessions/sessions.json
fi

echo ""
echo "✅ Migration complete!"
echo ""
echo "Summary:"
echo "  - All crons migrated to worker agent with DeepSeek"
echo "  - Zombie sessions cleaned"
echo "  - Old cron sessions removed"
echo ""
echo "Verify:"
echo "  npx clawdbot status --all"
echo "  npx clawdbot cron list"
echo ""
echo "Expected result:"
echo "  - 1 main session (your direct chats)"
echo "  - Worker sessions will appear as crons run"
echo "  - All on DeepSeek (10M free tokens/day)"
