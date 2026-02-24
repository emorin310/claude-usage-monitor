#!/bin/bash
# send-mqtt.sh - Send message to another bot
# Usage: ./send-mqtt.sh <recipient> <type> '<payload_json>'
# Example: ./send-mqtt.sh magi notification '{"event":"test"}'

set -e

MQTT_HOST="${MQTT_HOST:-192.168.1.151}"
MQTT_USER="${MQTT_USER:-mqtt}"
MQTT_PASS="${MQTT_PASS:-letx}"
BOT_NAME="${BOT_NAME:-marvin}"

RECIPIENT="$1"
TYPE="${2:-message}"
PAYLOAD="${3:-{}}"

if [ -z "$RECIPIENT" ]; then
  echo "Usage: $0 <recipient> [type] [payload_json]"
  echo "Recipients: marvin, magi, broadcast"
  exit 1
fi

MESSAGE=$(jq -n \
  --arg from "$BOT_NAME" \
  --arg ts "$(date -Iseconds)" \
  --arg type "$TYPE" \
  --argjson payload "$PAYLOAD" \
  '{from:$from, timestamp:$ts, type:$type, payload:$payload}')

mosquitto_pub -h "$MQTT_HOST" -u "$MQTT_USER" -P "$MQTT_PASS" \
  -t "bots/$RECIPIENT/inbox" \
  -m "$MESSAGE"

echo "Sent to bots/$RECIPIENT/inbox"
