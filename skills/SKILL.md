---
name: mqtt-bots
description: Inter-bot MQTT communication protocol for Marvin, Magi, and other agents.
version: 1.0.0
metadata:
  clawdis:
    emoji: "📡"
    requires:
      bins: ["mosquitto_pub", "mosquitto_sub", "jq"]
---

# MQTT Inter-Bot Communication

Standard protocol for bot-to-bot messaging via Home Assistant Mosquitto broker.

## Connection Details
```
Host: 192.168.1.151
Port: 1883
Username: mqtt
Password: letx
```

## Topic Structure
```
bots/
├── marvin/
│   └── inbox     # Marvin receives here
├── magi/
│   └── inbox     # Magi receives here
└── broadcast     # All bots subscribe
```

## Message Format
```json
{
  "from": "sender_name",
  "timestamp": "ISO8601",
  "type": "message_type",
  "payload": { ... }
}
```

### Message Types
| Type | Purpose |
|------|---------|
| `request` | Action request with payload |
| `response` | Reply to a request |
| `notification` | Async notification (download complete, etc.) |
| `status` | Bot status update |
| `setup_instructions` | Onboarding/config info |

## Send Message
```bash
mosquitto_pub -h 192.168.1.151 -u mqtt -P letx \
  -t "bots/<recipient>/inbox" \
  -m '{"from":"<sender>","timestamp":"'"$(date -Iseconds)"'","type":"request","payload":{...}}'
```

## Listen for Messages
```bash
mosquitto_sub -h 192.168.1.151 -u mqtt -P letx \
  -t "bots/<myname>/inbox" \
  -t "bots/broadcast"
```

## Helper Scripts

### send-mqtt.sh
```bash
#!/bin/bash
# Usage: ./send-mqtt.sh <recipient> <type> '<payload_json>'
RECIPIENT="$1"
TYPE="$2"
PAYLOAD="$3"
BOT_NAME="${BOT_NAME:-$(hostname)}"

mosquitto_pub -h 192.168.1.151 -u mqtt -P letx \
  -t "bots/$RECIPIENT/inbox" \
  -m "$(jq -n \
    --arg from "$BOT_NAME" \
    --arg ts "$(date -Iseconds)" \
    --arg type "$TYPE" \
    --argjson payload "$PAYLOAD" \
    '{from:$from, timestamp:$ts, type:$type, payload:$payload}')"
```

### receive-mqtt.sh
```bash
#!/bin/bash
# Usage: ./receive-mqtt.sh <botname>
BOT_NAME="$1"
mosquitto_sub -h 192.168.1.151 -u mqtt -P letx \
  -t "bots/$BOT_NAME/inbox" \
  -t "bots/broadcast"
```

## Media Request Actions (Marvin)
Send to `bots/marvin/inbox`:

### Request Movie
```json
{
  "from": "magi",
  "type": "request",
  "payload": {
    "action": "request_movie",
    "title": "Movie Name",
    "year": 2024,
    "requestedBy": "Username",
    "replySession": "magi"
  }
}
```

### Search Library
```json
{
  "payload": {
    "action": "search",
    "query": "movie name",
    "type": "movie"
  }
}
```

### Other Actions
- `search_tmdb` - Search TMDB
- `stats` - Library stats
- `weekly_stats` - Watch history
- `quickconnect` - Jellyfin auth code
- `check_status` - Download progress

## Response Format
Marvin sends to `bots/magi/inbox`:
```json
{
  "from": "marvin",
  "type": "response",
  "payload": {
    "status": "SUCCESS|ERROR|NOT_FOUND",
    "data": { ... },
    "message": "Human readable message"
  }
}
```

## Async Notifications
When a download completes:
```json
{
  "from": "marvin",
  "type": "notification",
  "payload": {
    "event": "download_complete",
    "title": "Movie Name",
    "year": 2024,
    "quality": "1080p",
    "message": "Movie Name (2024) is ready to watch! 🍿",
    "playUrl": "https://jellyfin.ericmorin.online/...",
    "requestedBy": "Username"
  }
}
```

## Bot Registry
| Bot | Host | Capabilities |
|-----|------|--------------|
| marvin | marvinbot (192.168.1.201) | media requests, homelab, monitoring |
| magi | magrathea (Eric's Mac) | family assistant, user-facing |

---
*Created: 2026-02-21*
