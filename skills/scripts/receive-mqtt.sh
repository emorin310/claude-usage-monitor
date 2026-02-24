#!/bin/bash
# receive-mqtt.sh - Listen for messages on bot inbox
# Usage: ./receive-mqtt.sh [botname]
# Example: ./receive-mqtt.sh magi

MQTT_HOST="${MQTT_HOST:-192.168.1.151}"
MQTT_USER="${MQTT_USER:-mqtt}"
MQTT_PASS="${MQTT_PASS:-letx}"
BOT_NAME="${1:-${BOT_NAME:-marvin}}"

echo "Listening on bots/$BOT_NAME/inbox and bots/broadcast..."
echo "Press Ctrl+C to stop"
echo "---"

mosquitto_sub -h "$MQTT_HOST" -u "$MQTT_USER" -P "$MQTT_PASS" \
  -t "bots/$BOT_NAME/inbox" \
  -t "bots/broadcast" \
  -v | while read -r topic message; do
    echo "[$(date +%H:%M:%S)] $topic"
    echo "$message" | jq '.' 2>/dev/null || echo "$message"
    echo "---"
done
