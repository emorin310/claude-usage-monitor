#!/bin/bash
# ha-scenes.sh - List all available scenes
# Usage: ./ha-scenes.sh [filter]

set -e

HA_URL="${HA_URL:-http://192.168.1.151:8123}"
HA_TOKEN="${HA_TOKEN}"

if [ -z "$HA_TOKEN" ]; then
  echo '{"status":"ERROR","message":"HA_TOKEN not set"}'
  exit 1
fi

FILTER="$1"

# Get all scenes
STATES=$(curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN")

if [ -z "$FILTER" ]; then
  echo "$STATES" | jq '[.[] | select(.entity_id | startswith("scene.")) | {
    scene_id: .entity_id,
    name: (.attributes.friendly_name // .entity_id),
    last_activated: .state
  }] | sort_by(.name)'
else
  echo "$STATES" | jq --arg pattern "$FILTER" '[.[] | select(.entity_id | startswith("scene.")) | select(.entity_id | test($pattern; "i")) | {
    scene_id: .entity_id,
    name: (.attributes.friendly_name // .entity_id)
  }]'
fi
