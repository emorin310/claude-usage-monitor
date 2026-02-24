#!/bin/bash
# MQTT Bot Listener
# Usage: ./listen.sh [--verbose]

MQTT_HOST="192.168.1.151"
MQTT_USER="mqtt"
MQTT_PASS="letx"
BOT_NAME="magi"

VERBOSE=false
if [ "$1" = "--verbose" ] || [ "$1" = "-v" ]; then
  VERBOSE=true
fi

echo "👂 Listening for MQTT messages..."
echo "   Inbox: bots/$BOT_NAME/inbox"
echo "   Broadcast: bots/broadcast"
echo ""

mosquitto_sub -h "$MQTT_HOST" -u "$MQTT_USER" -P "$MQTT_PASS" \
  -t "bots/$BOT_NAME/inbox" \
  -t "bots/broadcast" \
  -F '%I %t %p' | while read -r timestamp topic payload; do
  
  # Log to file
  mkdir -p ~/clawd-magi/logs
  echo "[$timestamp] $topic: $payload" >> ~/clawd-magi/logs/mqtt-received.log
  
  # Parse and display
  if [ "$VERBOSE" = true ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⏰ $timestamp"
    echo "📍 Topic: $topic"
    echo "📦 Payload:"
    echo "$payload" | jq . 2>/dev/null || echo "$payload"
    echo ""
  else
    FROM=$(echo "$payload" | jq -r '.from // "unknown"' 2>/dev/null || echo "unknown")
    MSG=$(echo "$payload" | jq -r '.message // .content' 2>/dev/null || echo "$payload")
    echo "[$timestamp] 💬 $FROM: $MSG"
  fi
done
