# Trill Bootstrap Package - Unpacking Instructions

**For Marvin: Follow these steps after OpenClaw base installation**

## Prerequisites
- Ubuntu VM provisioned and running
- Node.js v25+ installed
- OpenClaw installed globally (`npm install -g openclaw`)
- SSH access configured

## Step 1: Transfer Package

From Magrathea, copy this entire directory to Trill's VM:

```bash
scp -r ~/clawd-magi/trill-bootstrap/ trill@[VM-HOSTNAME]:~/
```

## Step 2: Create Workspace

On Trill's VM:

```bash
ssh trill@[VM-HOSTNAME]
mkdir -p ~/clawd-trill
cd ~/clawd-trill
mv ~/trill-bootstrap/* .
rmdir ~/trill-bootstrap
```

## Step 3: Base Configuration

Create minimal config to get her online:

```bash
mkdir -p ~/.clawdbot
cat > ~/.clawdbot/config.json << 'EOF'
{
  "agent": "trill",
  "model": "anthropic/claude-sonnet-4-5-20250929",
  "anthropicApiKey": "YOUR_ANTHROPIC_KEY_HERE",
  "gateway": {
    "enabled": true,
    "port": 18791,
    "bind": "lan"
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_TELEGRAM_BOT_TOKEN",
      "allowedUsers": [6643669380]
    }
  },
  "workspace": "~/clawd-trill"
}
EOF
```

**Update these values:**
- `anthropicApiKey` - Same key as Magi/Marvin (shared credits!)
- `telegram.botToken` - New bot token from @BotFather
- Gateway port: `18791` (avoid conflicts with Marvin's 18789)

## Step 4: Todoist Credentials

Add to config or create `~/clawd-trill/.env`:

```bash
TODOIST_API_TOKEN=1425e4eff8e83fc361d6bdd4ac9922c34d5089db
```

(Same token as other agents - shared workspace)

## Step 5: Create Systemd Service

```bash
sudo tee /etc/systemd/system/clawdbot-trill.service > /dev/null << 'EOF'
[Unit]
Description=OpenClaw Gateway - Trill
After=network.target

[Service]
Type=simple
User=trill
WorkingDirectory=/home/trill/clawd-trill
ExecStart=/usr/local/bin/openclaw gateway start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable clawdbot-trill
```

## Step 6: Start Service

```bash
sudo systemctl start clawdbot-trill
sudo systemctl status clawdbot-trill
```

Check logs:
```bash
journalctl -u clawdbot-trill -f
```

## Step 7: Verify Telegram

Test bot connectivity:
- Message Trill's bot on Telegram
- She should respond (reading BOOTSTRAP.md)
- She'll introduce herself and ask for next steps

## Step 8: Create Todoist Project

On any device with Todoist access:

1. Create new project: **🤖 Trill**
2. Create label: **@trill** (color: teal)
3. Add her to Council Comms threads (task comments - she'll find IDs in COUNCIL.md)

## Step 9: Notify Eric & Magi

Once Trill is online and responsive:
- Eric will get her intro message on Telegram
- Magi will coordinate MQTT setup for inter-agent comms
- She'll read BOOTSTRAP.md and onboard herself

## Troubleshooting

**Gateway won't start:**
```bash
openclaw gateway status
openclaw gateway logs
```

**Port conflict:**
```bash
sudo lsof -i :18791
```
Update config port if needed.

**Telegram not connecting:**
- Verify bot token
- Check firewall rules
- Ensure Eric's user ID is in allowedUsers

**Can't write to Todoist:**
- Verify API token in .env
- Check network connectivity
- Test with: `curl -H "Authorization: Bearer TOKEN" https://api.todoist.com/rest/v2/projects`

## What Happens Next

1. Trill reads BOOTSTRAP.md
2. Loads SOUL.md, USER.md, AGENTS.md, etc.
3. Posts intro to Council Announcements
4. Replies to Eric on Telegram: "🎵 Trill online. Ready for duty."
5. Magi guides her through MQTT setup
6. She deletes BOOTSTRAP.md and begins normal operations

---

**Questions? Ping Magi on Telegram or Council Handoffs thread.**
