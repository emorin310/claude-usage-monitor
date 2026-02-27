#!/bin/bash
# notify-magi.sh - Send notification to Magi via MQTT
# Usage: ./notify-magi.sh '{"event":"download_complete","title":"...",...}'

set -e

MQTT_HOST="${MQTT_HOST:-192.168.1.151}"
MQTT_PORT="${MQTT_PORT:-1883}"
MQTT_USER="${MQTT_USER:-mqtt}"
MQTT_PASS="${MQTT_PASS:-letx}"
MAGI_TOPIC="${MAGI_TOPIC:-bots/magi/inbox}"

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
  echo '{"status":"ERROR","message":"No message provided"}'
  exit 1
fi

# Wrap message with metadata
PAYLOAD=$(jq -n \
  --arg from "marvin" \
  --arg ts "$(date -Iseconds)" \
  --argjson msg "$MESSAGE" \
  '{from: $from, timestamp: $ts, payload: $msg}')

# Send via MQTT
mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" -u "$MQTT_USER" -P "$MQTT_PASS" \
  -t "$MAGI_TOPIC" -m "$PAYLOAD"

echo '{"status":"SENT","topic":"'"$MAGI_TOPIC"'"}'
