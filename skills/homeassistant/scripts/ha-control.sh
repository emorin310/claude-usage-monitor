#!/bin/bash
# ha-control.sh - Turn on/off/toggle entities
# Usage: ./ha-control.sh <on|off|toggle> <entity_id>

set -e

HA_URL="${HA_URL:-http://192.168.1.151:8123}"
HA_TOKEN="${HA_TOKEN}"

if [ -z "$HA_TOKEN" ]; then
  echo '{"status":"ERROR","message":"HA_TOKEN not set"}'
  exit 1
fi

ACTION="$1"
ENTITY="$2"

if [ -z "$ACTION" ] || [ -z "$ENTITY" ]; then
  echo '{"status":"ERROR","message":"Usage: ha-control.sh <on|off|toggle> <entity_id>"}'
  exit 1
fi

# Determine domain from entity_id
DOMAIN=$(echo "$ENTITY" | cut -d. -f1)

# Map action to service
case "$ACTION" in
  on)
    SERVICE="turn_on"
    ;;
  off)
    SERVICE="turn_off"
    ;;
  toggle)
    SERVICE="toggle"
    ;;
  *)
    echo '{"status":"ERROR","message":"Invalid action. Use: on, off, toggle"}'
    exit 1
    ;;
esac

# Call the service
RESULT=$(curl -s -X POST "$HA_URL/api/services/$DOMAIN/$SERVICE" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"entity_id\": \"$ENTITY\"}")

# Get new state
sleep 0.5
NEW_STATE=$(curl -s "$HA_URL/api/states/$ENTITY" -H "Authorization: Bearer $HA_TOKEN" | jq -r '.state')

echo "{\"status\":\"SUCCESS\",\"entity\":\"$ENTITY\",\"action\":\"$SERVICE\",\"new_state\":\"$NEW_STATE\"}"
