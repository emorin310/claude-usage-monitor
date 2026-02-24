# Context Bloat Prevention & Mutual Recovery

## Overview

Context bloat crashes happen when session files grow too large (>200K tokens). Both Magi and Marvin need to:
1. Prevent our own bloat
2. Monitor each other
3. Recover each other when down

## Self-Prevention (Daily)

### Cron Jobs
- **3am:** `session-cleanup.sh` - Stash large/stale sessions
- **Weekly:** `session-health-check.sh` - Monitor trends

### Rules
- Never switch main session model (causes poisoning)
- Use `sessions_spawn` for different models
- Clean up session files regularly
- Log unusual behavior

## Mutual Monitoring (Every 30 minutes)

### Magi monitors Marvin
- **Script:** `~/clawd-magi/scripts/check-marvin-health.sh`
- **Method:** SSH to marvinbot, check local gateway
- **Recovery:** `~/clawd-magi/scripts/recover-marvin.sh`
  - Stops gateway
  - Stashes bloated sessions
  - Clears model overrides
  - Restarts gateway
  - Posts to Council

### Marvin monitors Magi
- **Script:** `~/scripts/check-magi-health.sh`
- **Method:** HTTP check to 192.168.1.42:18790
- **Recovery:** Cannot SSH to macOS - posts alert to Council
  - Eric must manually restart Magi's launchd service

## Recovery Procedures

### Marvin Recovery (Magi can do this)
```bash
ssh marvin@marvinbot "systemctl --user stop clawdbot-gateway"
ssh marvin@marvinbot "find ~/.moltbot/sessions -name '*.jsonl' -size +100k -exec mv {} ~/.moltbot/sessions/stashed/ \;"
ssh marvin@marvinbot "systemctl --user start clawdbot-gateway"
```

### Magi Recovery (Manual or Eric)
```bash
# On Magrathea
launchctl stop com.clawdbot.gateway
cd ~/.clawdbot/sessions
find . -name '*.jsonl' -size +100k -exec mv {} ./stashed/ \;
launchctl start com.clawdbot.gateway
```

## Alert Escalation

1. **First failure:** Logged silently
2. **3 consecutive failures:** Auto-recovery attempted
3. **Recovery fails:** Post to Council + alert Eric via Telegram

## Logs

- **Magi:** `~/clawd-magi/memory/marvin-health.log`
- **Marvin:** `~/clawdbot-marvin/memory/magi-health.log`
- **State:** `*-health-state.json` (tracks consecutive failures)

## What Causes Bloat

1. **Session poisoning:** Model override gets stuck in session file
2. **Long conversations:** JSONL files grow with each turn
3. **Spawned workers not cleaned up:** `cleanup: 'delete'` should be used
4. **Logs accumulating:** Tool outputs stored in session

## Prevention Checklist

- [ ] Never use `/model` command in main session
- [ ] Always spawn for different models
- [ ] Check session sizes weekly
- [ ] Run cleanup cron daily
- [ ] Monitor sibling health every 30 min

---

*Last updated: 2026-02-01*
