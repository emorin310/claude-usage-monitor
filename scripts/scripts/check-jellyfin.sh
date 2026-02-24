#!/bin/bash
# check-jellyfin.sh - Verify movie is available in Jellyfin
# Usage: ./check-jellyfin.sh "Movie Title" [year]
# Returns JSON: {status, title, jellyfinId, year, message}

set -e

JELLYFIN_URL="${JELLYFIN_URL:-http://192.168.1.96:8096}"
JELLYFIN_KEY="${JELLYFIN_KEY:-c5b4d7fc157b49778470414e5944b0b2}"

TITLE="$1"
YEAR="$2"

if [ -z "$TITLE" ]; then
  echo '{"status":"ERROR","message":"Usage: check-jellyfin.sh \"Movie Title\" [year]"}'
  exit 1
fi

# URL encode the title (use printf to avoid trailing newline)
ENCODED_TITLE=$(printf '%s' "$TITLE" | jq -sRr @uri)

# Search Jellyfin
SEARCH_RESULT=$(curl -s -m 10 -H "X-Emby-Token: $JELLYFIN_KEY" \
  "$JELLYFIN_URL/Items?searchTerm=$ENCODED_TITLE&IncludeItemTypes=Movie&Recursive=true&Limit=5" 2>/dev/null)

if [ -z "$SEARCH_RESULT" ]; then
  echo '{"status":"ERROR","message":"Could not connect to Jellyfin"}'
  exit 1
fi

# Parse results
TOTAL=$(echo "$SEARCH_RESULT" | jq '.TotalRecordCount // 0')

if [ "$TOTAL" = "0" ]; then
  echo '{"status":"NOT_FOUND","title":"'"$TITLE"'","message":"Not in Jellyfin library"}'
  exit 0
fi

# Find best match (year match preferred)
if [ -n "$YEAR" ]; then
  MATCH=$(echo "$SEARCH_RESULT" | jq --arg year "$YEAR" '[.Items[] | select(.ProductionYear == ($year | tonumber))][0] // .Items[0]')
else
  MATCH=$(echo "$SEARCH_RESULT" | jq '.Items[0]')
fi

JF_TITLE=$(echo "$MATCH" | jq -r '.Name')
JF_YEAR=$(echo "$MATCH" | jq -r '.ProductionYear // "Unknown"')
JF_ID=$(echo "$MATCH" | jq -r '.Id')
JF_RATING=$(echo "$MATCH" | jq -r '.OfficialRating // "NR"')

echo '{"status":"AVAILABLE","title":"'"$JF_TITLE"'","year":'"$JF_YEAR"',"jellyfinId":"'"$JF_ID"'","rating":"'"$JF_RATING"'","message":"Available in Jellyfin"}'
