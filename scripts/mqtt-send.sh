#!/bin/bash
# Send MQTT message to another bot
# Usage: ./mqtt-send.sh <recipient> <type> '<payload_json>'

RECIPIENT="$1"
TYPE="$2"
PAYLOAD="$3"

if [ -z "$RECIPIENT" ] || [ -z "$TYPE" ] || [ -z "$PAYLOAD" ]; then
    echo "Usage: $0 <recipient> <type> '<payload_json>'"
    exit 1
fi

# Use -c for compact output (single line)
MSG=$(jq -c -n \
    --arg from "magi" \
    --arg ts "$(date -Iseconds)" \
    --arg type "$TYPE" \
    --argjson payload "$PAYLOAD" \
    '{from:$from, timestamp:$ts, type:$type, payload:$payload}')

mosquitto_pub -h 192.168.1.151 -u mqtt -P letx \
  -t "bots/$RECIPIENT/inbox" \
  -m "$MSG"

echo "✅ Sent $TYPE to bots/$RECIPIENT/inbox"
