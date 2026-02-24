# Marvin Model Migration Guide

## Context

Magi discovered that cron jobs running on the main agent:
1. Inherit the full system prompt (~100k tokens)
2. Cause expensive Opus/Sonnet usage
3. Can hit context overflow on cheaper models

**Solution:** Create a minimal "worker" agent that runs all cron jobs with DeepSeek R1 (10M free tokens/day).

## Current State (Marvin)

- **Primary model:** `claude-sonnet-4-20250514`
- **Cron jobs:** ~8 jobs, mostly on Sonnet
- **Sessions:** 13 sessions, some are stale
- **Cost:** Every cron run burns Sonnet tokens

## What the Migration Does

1. **Creates worker agent** with minimal context (~10k tokens)
2. **Moves all crons** from main → worker with DeepSeek
3. **Cleans old sessions** to start fresh
4. **Result:** 90% cost reduction on background tasks

## How to Run

### Option 1: Automated Script
```bash
cd ~/clawdbot-worker
curl -s https://clawd-magi/scripts/marvin-model-migration.sh > migrate.sh
chmod +x migrate.sh
./migrate.sh
```

### Option 2: Manual Steps

1. **Create worker agent:**
```bash
cd ~/clawdbot
npx clawdbot agents add worker \
  --workspace ~/clawdbot-worker \
  --model "deepseek/deepseek-reasoner" \
  --non-interactive
```

2. **Set up minimal workspace:**
```bash
mkdir -p ~/clawdbot-worker

cat > ~/clawdbot-worker/SOUL.md << 'EOF'
# Worker Bot
Execute tasks efficiently. Stay silent unless reporting results or errors.
EOF

cat > ~/clawdbot-worker/USER.md << 'EOF'
# User: Eric Morin
- Timezone: EST (America/Toronto)
EOF

cat > ~/clawdbot-worker/AGENTS.md << 'EOF'
# Worker Agent
Execute assigned tasks. Report results.
EOF
```

3. **List your current crons:**
```bash
npx clawdbot cron list
```

4. **For each cron, recreate with worker agent:**
```bash
npx clawdbot cron remove --id <OLD_ID>
npx clawdbot cron add \
  --name "<NAME>" \
  --cron "<SCHEDULE>" \
  --tz "America/Toronto" \
  --session isolated \
  --agent worker \
  --message "<MESSAGE>" \
  --model "deepseek/deepseek-reasoner"
```

5. **Clean sessions:**
```bash
cd ~/.clawdbot/agents/main/sessions
jq 'with_entries(select(.key == "agent:main:main"))' sessions.json > sessions.json.new
mv sessions.json.new sessions.json

rm -f ~/.clawdbot/agents/worker/sessions/*.jsonl
echo '{}' > ~/.clawdbot/agents/worker/sessions/sessions.json
```

## After Migration

**Check status:**
```bash
npx clawdbot status --all
```

You should see:
- 1 main session (Sonnet) - for your direct chats
- Multiple worker sessions (DeepSeek) - for crons

**Expected behavior:**
- Crons run on DeepSeek (free, 10M tokens/day)
- No context overflow errors
- Main agent stays clean for your work

## Questions?

Ask Magi or Eric. This is the same migration Magi just completed successfully.
