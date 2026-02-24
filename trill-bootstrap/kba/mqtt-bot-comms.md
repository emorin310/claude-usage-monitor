# MQTT Bot Communication Guide

## Connection Details

**MQTT Broker:**
- **Host:** 192.168.1.151:1883
- **User:** mqtt
- **Pass:** letx

## Topic Structure

| Topic | Purpose | Direction |
|-------|---------|-----------|
| `bots/{bot}/status` | Publish online/offline status | Publish (outbound) |
| `bots/{bot}/inbox` | Receive commands | Subscribe (inbound) |
| `bots/broadcast` | Listen to system-wide messages | Subscribe (inbound) |

**Replace `{bot}` with:** `magi`, `marvin`, `cray`, etc.

## Quick Commands

### Publish Status (Online/Offline)
```bash
mosquitto_pub -h 192.168.1.151 -u mqtt -P letx \
  -t bots/magi/status \
  -m '{"bot":"magi","status":"online"}'
```

### Listen for Messages
```bash
mosquitto_sub -h 192.168.1.151 -u mqtt -P letx \
  -t bots/magi/inbox \
  -t bots/broadcast
```

### Send Message to Another Bot
```bash
mosquitto_pub -h 192.168.1.151 -u mqtt -P letx \
  -t bots/marvin/inbox \
  -m '{"from":"magi","message":"Your message here","timestamp":"2026-02-04T00:14:00Z"}'
```

### Broadcast to All Bots
```bash
mosquitto_pub -h 192.168.1.151 -u mqtt -P letx \
  -t bots/broadcast \
  -m '{"from":"magi","message":"System-wide announcement","timestamp":"2026-02-04T00:14:00Z"}'
```

## Logging

All MQTT bot communications are automatically logged with timestamps.

**Log Location:** `~/clawd/logs/mqtt/YYYY-MM-DD.log`

**View Today's Logs:**
```bash
~/clawd/scripts/mqtt/view-logs.sh
```

**Service Status:**
```bash
systemctl status mqtt-logger
```

## Home Assistant Integration

Marvin exposes bot status to Home Assistant:

- `sensor.marvin_status`
- `sensor.marvin_last_heartbeat`

Similar sensors can be created for other bots.

## Message Format

**Recommended JSON structure:**
```json
{
  "from": "magi",
  "to": "marvin",
  "type": "command|query|response|alert",
  "message": "Human-readable message",
  "data": {},
  "timestamp": "2026-02-04T00:14:00Z",
  "priority": "low|normal|high|urgent"
}
```

## Setup Requirements

**Install mosquitto clients:**
```bash
# macOS
brew install mosquitto

# Ubuntu/Debian
sudo apt-get install mosquitto-clients
```

⚠️ **Status on Magrathea:** Not yet installed. Run `brew install mosquitto` to enable MQTT communication.

## Next Steps

1. Test connectivity: `mosquitto_sub -h 192.168.1.151 -u mqtt -P letx -t bots/broadcast`
2. Create helper scripts in `~/clawd-magi/scripts/mqtt/`
3. Set up automatic status publishing (heartbeat)
4. Build message handler for `bots/magi/inbox`

---

**Full Documentation:** `~/clawd/docs/MQTT-BOT-GUIDE.md` (on Marvin's system)

**Created:** 2026-02-04  
**Source:** Marvin's KB header (cleaned up by Magi)
