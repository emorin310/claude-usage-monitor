#!/bin/bash
# MQTT Bot Communication Helper
# Usage: ./send.sh <bot> <message>
#   or:  ./send.sh --broadcast <message>

MQTT_HOST="192.168.1.151"
MQTT_USER="mqtt"
MQTT_PASS="letx"
FROM_BOT="magi"

if [ "$1" = "--broadcast" ]; then
  TARGET_TOPIC="bots/broadcast"
  TO_BOT="all"
  MESSAGE="$2"
elif [ -z "$2" ]; then
  echo "Usage: $0 <bot> <message>"
  echo "   or: $0 --broadcast <message>"
  exit 1
else
  TO_BOT="$1"
  TARGET_TOPIC="bots/$TO_BOT/inbox"
  MESSAGE="$2"
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

PAYLOAD=$(cat <<EOF
{
  "from": "$FROM_BOT",
  "to": "$TO_BOT",
  "type": "message",
  "message": "$MESSAGE",
  "timestamp": "$TIMESTAMP"
}
EOF
)

echo "📤 Sending to $TO_BOT via MQTT..."
mosquitto_pub -h "$MQTT_HOST" -u "$MQTT_USER" -P "$MQTT_PASS" \
  -t "$TARGET_TOPIC" \
  -m "$PAYLOAD"

if [ $? -eq 0 ]; then
  echo "✅ Sent successfully"
  echo "$TIMESTAMP [$FROM_BOT → $TO_BOT]: $MESSAGE" >> ~/clawd/logs/mqtt-sent.log
else
  echo "❌ Failed to send"
  exit 1
fi
