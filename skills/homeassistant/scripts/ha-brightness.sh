#!/bin/bash
# ha-brightness.sh - Set light brightness
# Usage: ./ha-brightness.sh <entity_id> <percent>

set -e

HA_URL="${HA_URL:-http://192.168.1.151:8123}"
HA_TOKEN="${HA_TOKEN}"

if [ -z "$HA_TOKEN" ]; then
  echo '{"status":"ERROR","message":"HA_TOKEN not set"}'
  exit 1
fi

ENTITY="$1"
PERCENT="$2"

if [ -z "$ENTITY" ] || [ -z "$PERCENT" ]; then
  echo '{"status":"ERROR","message":"Usage: ha-brightness.sh <entity_id> <percent>"}'
  exit 1
fi

# Validate percent
if ! [[ "$PERCENT" =~ ^[0-9]+$ ]] || [ "$PERCENT" -lt 0 ] || [ "$PERCENT" -gt 100 ]; then
  echo '{"status":"ERROR","message":"Brightness must be 0-100"}'
  exit 1
fi

# Add light. prefix if not present
if [[ ! "$ENTITY" == light.* ]]; then
  ENTITY="light.$ENTITY"
fi

# Call light service with brightness
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"entity_id\": \"$ENTITY\", \"brightness_pct\": $PERCENT}" > /dev/null

# Get new state
sleep 0.5
STATE=$(curl -s "$HA_URL/api/states/$ENTITY" -H "Authorization: Bearer $HA_TOKEN")
NEW_STATE=$(echo "$STATE" | jq -r '.state')
NEW_BRIGHTNESS=$(echo "$STATE" | jq -r '.attributes.brightness // 0')
BRIGHTNESS_PCT=$(echo "scale=0; $NEW_BRIGHTNESS * 100 / 255" | bc 2>/dev/null || echo "$PERCENT")

echo "{\"status\":\"SUCCESS\",\"entity\":\"$ENTITY\",\"state\":\"$NEW_STATE\",\"brightness_pct\":$BRIGHTNESS_PCT}"
