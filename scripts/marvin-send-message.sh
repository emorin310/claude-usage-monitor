#!/usr/bin/env bash
# marvin-send-message.sh - Send messages to Marvin via gateway wake event
# Usage: ./marvin-send-message.sh "Your message here"

set -euo pipefail

MARVIN_URL="http://192.168.1.201:18790"
MARVIN_TOKEN="405987e5394153113d7284c99b2d1a1e70d6b6daf92abd80"
LOG_FILE="$HOME/clawd/marvin.md.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ $# -eq 0 ]; then
  echo "Usage: $0 \"message\""
  exit 1
fi

MESSAGE="$1"

# Log outgoing
echo "[$TIMESTAMP] [MAGI → MARVIN] $MESSAGE" >> "$LOG_FILE"

# Send via gateway cron wake event
# This triggers Marvin's heartbeat/wake handler with the message
RESPONSE=$(curl -s -X POST "$MARVIN_URL/api/cron/wake" \
  -H "Authorization: Bearer $MARVIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"📨 Message from Magi: $MESSAGE\",
    \"mode\": \"now\"
  }" 2>&1)

if echo "$RESPONSE" | grep -q '"ok":true'; then
  echo "✅ Message sent to Marvin"
  echo "[$TIMESTAMP] [SYSTEM] Message delivered via wake event" >> "$LOG_FILE"
else
  echo "❌ Failed to send message"
  echo "Response: $RESPONSE"
  echo "[$TIMESTAMP] [ERROR] Message delivery failed: $RESPONSE" >> "$LOG_FILE"
fi
