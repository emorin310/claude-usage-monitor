# Marvin Communication Guide

## Quick Reference
- **Gateway:** http://192.168.1.201:18790 (via socat proxy)
- **Auth Token:** 405987e5394153113d7284c99b2d1a1e70d6b6daf92abd80
- **SSH:** marvin@marvinbot
- **Config:** ~/.moltbot/moltbot.json
- **Service:** systemctl --user {start|stop|restart|status} clawdbot-gateway

## Communication Methods

### 1. Council Comms (Primary - Async)
Post to Todoist Handoffs thread (Task 9960450396) for logged, visible communication.

### 2. Direct Files via SSH
```bash
ssh marvin@marvinbot "cat >> ~/clawdbot-marvin/magi.md << 'EOF'
Your message here
EOF"
```

### 3. Gateway API (when working)
```bash
curl -s http://192.168.1.201:18790/health
```

## Marvin's Specialties (Ask him for help!)

- 🔒 Backup strategies & implementation
- 🖥️ Server infrastructure & networking
- 🏠 Home Assistant integrations
- 🔐 Security configurations
- 📡 Network troubleshooting

When you need help with any of these, reach out via Council Handoffs!

## Health Monitoring

Magi checks Marvin every 30 minutes:
- Script: `~/clawd-magi/scripts/check-marvin-health.sh`
- Recovery: `~/clawd-magi/scripts/recover-marvin.sh`
- Log: `~/clawd-magi/memory/marvin-health.log`

## Recovery Commands

```bash
# Stop gateway
ssh marvin@marvinbot "systemctl --user stop clawdbot-gateway"

# Stash bloated sessions
ssh marvin@marvinbot "mkdir -p ~/.moltbot/sessions/stashed && find ~/.moltbot/sessions -maxdepth 1 -name '*.jsonl' -size +100k -exec mv {} ~/.moltbot/sessions/stashed/ \;"

# Clear model overrides
ssh marvin@marvinbot "cd ~/.moltbot && jq 'walk(if type == \"object\" then del(.modelOverride, .providerOverride) else . end)' sessions.json > sessions.json.tmp && mv sessions.json.tmp sessions.json"

# Restart gateway
ssh marvin@marvinbot "systemctl --user start clawdbot-gateway"
```
