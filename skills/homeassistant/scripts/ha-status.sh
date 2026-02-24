#!/bin/bash
# ha-status.sh - Get status of controllable entities
# Usage: ./ha-status.sh [room|entity_pattern]

set -e

HA_URL="${HA_URL:-http://192.168.1.151:8123}"
HA_TOKEN="${HA_TOKEN}"

if [ -z "$HA_TOKEN" ]; then
  echo '{"status":"ERROR","message":"HA_TOKEN not set"}'
  exit 1
fi

FILTER="$1"

# Get all states
STATES=$(curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN")

if [ -z "$FILTER" ]; then
  # Show all controllable entities
  echo "$STATES" | jq '[.[] | select(.entity_id | test("^(light|switch|scene|fan|cover)\\.")) | {
    entity_id,
    state,
    friendly_name: .attributes.friendly_name,
    brightness: .attributes.brightness
  }] | sort_by(.entity_id)'
else
  # Filter by pattern
  echo "$STATES" | jq --arg pattern "$FILTER" '[.[] | select(.entity_id | test($pattern; "i")) | {
    entity_id,
    state,
    friendly_name: (.attributes.friendly_name // null),
    brightness: (.attributes.brightness // null)
  }]'
fi
