#!/bin/bash
# Marvin Model Migration Script
# Migrates cron jobs from main agent to worker agent with DeepSeek

set -e

echo "🔧 Marvin Model Migration"
echo "========================"
echo ""

cd ~/clawdbot

# 1. Create worker agent
echo "1. Creating worker agent..."
npx clawdbot agents add worker \
  --workspace ~/clawdbot-worker \
  --model "deepseek/deepseek-reasoner" \
  --non-interactive \
  --json

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

# 3. Get list of current cron jobs
echo "3. Checking current cron jobs..."
npx clawdbot cron list --json > /tmp/marvin-crons.json

# 4. Recreate each cron on worker agent with DeepSeek
echo "4. Migrating cron jobs to worker agent..."
jq -r '.jobs[] | "\(.id)|\(.name)|\(.schedule.expr)|\(.payload.message)"' /tmp/marvin-crons.json | while IFS='|' read -r id name schedule message; do
  echo "  - Removing old: $name"
  npx clawdbot cron remove --id "$id" || true
  
  echo "  - Creating new: $name"
  npx clawdbot cron add \
    --name "$name" \
    --cron "$schedule" \
    --tz "America/Toronto" \
    --session isolated \
    --agent worker \
    --message "$message" \
    --model "deepseek/deepseek-reasoner"
done

# 5. Clean old sessions (keep only main)
echo "5. Cleaning old sessions..."
cd ~/.clawdbot/agents/main/sessions
jq 'with_entries(select(.key == "agent:main:main"))' sessions.json > sessions.json.new
mv sessions.json.new sessions.json

# 6. Clean worker sessions
rm -f ~/.clawdbot/agents/worker/sessions/*.jsonl
echo '{}' > ~/.clawdbot/agents/worker/sessions/sessions.json

echo ""
echo "✅ Migration complete!"
echo ""
echo "Check status: npx clawdbot status --all"
echo "List crons: npx clawdbot cron list"
