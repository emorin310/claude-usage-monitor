#!/bin/bash
# ha-scene.sh - Activate a scene
# Usage: ./ha-scene.sh <scene_name>

set -e

HA_URL="${HA_URL:-http://192.168.1.151:8123}"
HA_TOKEN="${HA_TOKEN}"

if [ -z "$HA_TOKEN" ]; then
  echo '{"status":"ERROR","message":"HA_TOKEN not set"}'
  exit 1
fi

SCENE="$1"

if [ -z "$SCENE" ]; then
  echo '{"status":"ERROR","message":"Usage: ha-scene.sh <scene_name>"}'
  exit 1
fi

# Add scene. prefix if not present
if [[ ! "$SCENE" == scene.* ]]; then
  SCENE="scene.$SCENE"
fi

# Call scene service
RESULT=$(curl -s -w "\n%{http_code}" -X POST "$HA_URL/api/services/scene/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"entity_id\": \"$SCENE\"}")

HTTP_CODE=$(echo "$RESULT" | tail -1)
BODY=$(echo "$RESULT" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
  echo "{\"status\":\"SUCCESS\",\"scene\":\"$SCENE\",\"message\":\"Scene activated\"}"
elif [ "$HTTP_CODE" = "400" ]; then
  echo "{\"status\":\"ERROR\",\"message\":\"Scene not found: $SCENE\"}"
else
  echo "{\"status\":\"ERROR\",\"httpCode\":\"$HTTP_CODE\",\"message\":\"Failed to activate scene\"}"
fi
