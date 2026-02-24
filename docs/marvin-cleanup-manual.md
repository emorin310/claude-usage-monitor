# Marvin Manual Cleanup Guide

## Problem
Marvin has 10+ sessions, most running on expensive models (Sonnet). Need to clean zombies and migrate crons to worker agent.

## Step 1: Clean Zombie Sessions

Zombie sessions identified:
- `d522b946-eba7-4d91-9bbc-2f3b20046e3c` (not in cron list)
- `1f6b013a-20...` (old subagent on grok-3)

```bash
cd ~/.clawdbot/agents/main/sessions

# Backup first
cp sessions.json sessions.json.backup-$(date +%Y%m%d-%H%M%S)

# Remove zombies
jq 'del(.["agent:main:cron:d522b946-eba7-4d91-9bbc-2f3b20046e3c"]) | 
    del(.["agent:main:subagent:1f6b013a-2085-4f2f-b768-1c11de5fafe3"])' \
    sessions.json > sessions.json.new

mv sessions.json.new sessions.json
```

## Step 2: Verify Active Crons

List current crons:
```bash
cd ~/.clawdbot/cron
jq '.jobs[] | {id, name, agentId}' jobs.json
```

All 10 should show `"agentId": "main"` - that's the problem!

## Step 3: Create Worker Agent

```bash
cd ~/clawdbot
npx clawdbot agents add worker \
  --workspace ~/clawdbot-worker \
  --model "deepseek/deepseek-reasoner" \
  --non-interactive
```

## Step 4: Set Up Worker Workspace

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

## Step 5: Migrate Crons (One at a Time)

For EACH cron job, run these commands:

### Example: kanban-watch

```bash
cd ~/clawdbot

# Get the old job details
npx clawdbot cron list | grep kanban-watch

# Remove old
npx clawdbot cron remove --id 49765e77-5c17-4e31-8374-afb3955277d2

# Create new with worker agent
npx clawdbot cron add \
  --name "kanban-watch" \
  --cron "*/5 * * * *" \
  --tz "America/Toronto" \
  --session isolated \
  --agent worker \
  --message "<original message>" \
  --model "deepseek/deepseek-reasoner"
```

Repeat for all 10 crons:
1. kanban-watch
2. Weekly Infrastructure Health Check
3. Daily Backup Verification
4. SSL Certificate Expiry Check
5. Daily Storage Monitor
6. Docker Container Health
7. UPS Battery Monitor
8. Weekly Security Audit
9. Claude Credit Monitor
10. Kanban-Todoist Sync

## Step 6: Clean All Old Sessions

After migrating all crons:

```bash
cd ~/.clawdbot/agents/main/sessions

# Keep only main session
jq 'with_entries(select(.key == "agent:main:main"))' \
    sessions.json > sessions.json.clean

mv sessions.json.clean sessions.json

# Clean worker (fresh start)
rm -f ~/.clawdbot/agents/worker/sessions/*.jsonl
echo '{}' > ~/.clawdbot/agents/worker/sessions/sessions.json
```

## Step 7: Verify

```bash
npx clawdbot status --all
npx clawdbot cron list
```

**Expected result:**
- 1 main session (Sonnet) - for direct chats
- 0 worker sessions initially (will populate as crons run)
- All 10 crons showing `agentId: worker` and `model: deepseek/deepseek-reasoner`

## Troubleshooting

**If npx hangs:**
- Use `timeout 30 npx ...` to auto-kill after 30s
- Or edit `~/.clawdbot/cron/jobs.json` directly

**If worker agent creation fails:**
- Check if it already exists: `ls ~/.clawdbot/agents/`
- If exists, just use it (skip agent creation)

**If you get lost:**
- Restore from backup: `cp sessions.json.backup-* sessions.json`
- Ask Magi for help via Council
