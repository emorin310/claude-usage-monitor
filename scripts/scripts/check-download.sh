#!/bin/bash
# check-download.sh - Check download status by radarrId or title
# Usage: ./check-download.sh <radarrId>
#        ./check-download.sh --title "Movie Title"
# Returns JSON: {status, title, progress, eta, quality, message}

set -e

RADARR_URL="${RADARR_URL:-http://10.15.40.89:7878}"
RADARR_KEY="${RADARR_KEY:-9357c52a8209410cbfabb2cdad6480bf}"

if [ "$1" = "--title" ]; then
  # Search by title
  TITLE="$2"
  MOVIE=$(curl -s -m 10 -H "X-Api-Key: $RADARR_KEY" \
    "$RADARR_URL/api/v3/movie" | jq '.[] | select(.title | test("'"$TITLE"'"; "i")) | .[0]' 2>/dev/null)
  RADARR_ID=$(echo "$MOVIE" | jq -r '.id // empty')
elif [ -n "$1" ]; then
  RADARR_ID="$1"
else
  echo '{"status":"ERROR","message":"Usage: check-download.sh <radarrId> or --title \"Movie\""}'
  exit 1
fi

if [ -z "$RADARR_ID" ]; then
  echo '{"status":"NOT_FOUND","message":"Movie not found in Radarr"}'
  exit 0
fi

# Get movie info
MOVIE=$(curl -s -m 10 -H "X-Api-Key: $RADARR_KEY" \
  "$RADARR_URL/api/v3/movie/$RADARR_ID")

TITLE=$(echo "$MOVIE" | jq -r '.title')
HAS_FILE=$(echo "$MOVIE" | jq -r '.hasFile')
MONITORED=$(echo "$MOVIE" | jq -r '.monitored')

if [ "$HAS_FILE" = "true" ]; then
  FILE_SIZE=$(echo "$MOVIE" | jq -r '.movieFile.size // 0')
  QUALITY=$(echo "$MOVIE" | jq -r '.movieFile.quality.quality.name // "Unknown"')
  SIZE_GB=$(echo "scale=2; $FILE_SIZE / 1073741824" | bc 2>/dev/null || echo "?")
  echo '{"status":"DOWNLOADED","title":"'"$TITLE"'","radarrId":'"$RADARR_ID"',"quality":"'"$QUALITY"'","sizeGB":"'"$SIZE_GB"'","message":"Downloaded and ready"}'
  exit 0
fi

# Check queue for active download
QUEUE=$(curl -s -m 10 -H "X-Api-Key: $RADARR_KEY" \
  "$RADARR_URL/api/v3/queue?movieId=$RADARR_ID")

QUEUE_ITEM=$(echo "$QUEUE" | jq '.records[0] // empty')

if [ -n "$QUEUE_ITEM" ] && [ "$QUEUE_ITEM" != "null" ]; then
  PROGRESS=$(echo "$QUEUE_ITEM" | jq -r '(100 - (.sizeleft / .size * 100)) | floor')
  ETA=$(echo "$QUEUE_ITEM" | jq -r '.timeleft // "Unknown"')
  QUALITY=$(echo "$QUEUE_ITEM" | jq -r '.quality.quality.name // "Unknown"')
  STATUS=$(echo "$QUEUE_ITEM" | jq -r '.status')
  echo '{"status":"DOWNLOADING","title":"'"$TITLE"'","radarrId":'"$RADARR_ID"',"progress":'"$PROGRESS"',"eta":"'"$ETA"'","quality":"'"$QUALITY"'","downloadStatus":"'"$STATUS"'"}'
else
  if [ "$MONITORED" = "true" ]; then
    echo '{"status":"SEARCHING","title":"'"$TITLE"'","radarrId":'"$RADARR_ID"',"message":"Monitored, searching for releases"}'
  else
    echo '{"status":"NOT_MONITORED","title":"'"$TITLE"'","radarrId":'"$RADARR_ID"',"message":"Not monitored"}'
  fi
fi
