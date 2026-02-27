#!/bin/bash
# check-pending.sh - Check pending requests and notify on completion
# Run via cron every minute: * * * * * /path/to/check-pending.sh
# Returns JSON with notifications that need to be sent

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
PENDING_FILE="$DATA_DIR/pending-requests.json"
NOTIFY_FILE="$DATA_DIR/notifications.jsonl"

# Initialize files if needed
[ -f "$PENDING_FILE" ] || echo '{}' > "$PENDING_FILE"

PENDING=$(cat "$PENDING_FILE")
KEYS=$(echo "$PENDING" | jq -r 'keys[]')

if [ -z "$KEYS" ]; then
  # No pending requests
  exit 0
fi

UPDATED_PENDING="$PENDING"
NOTIFICATIONS=""

for RADARR_ID in $KEYS; do
  REQUEST=$(echo "$PENDING" | jq --arg id "$RADARR_ID" '.[$id]')
  TITLE=$(echo "$REQUEST" | jq -r '.title')
  YEAR=$(echo "$REQUEST" | jq -r '.year')
  REQUESTED_BY=$(echo "$REQUEST" | jq -r '.requestedBy')
  REPLY_SESSION=$(echo "$REQUEST" | jq -r '.replySession')
  
  # Check download status
  DOWNLOAD_STATUS=$("$SCRIPT_DIR/check-download.sh" "$RADARR_ID" 2>/dev/null || echo '{"status":"ERROR"}')
  STATUS=$(echo "$DOWNLOAD_STATUS" | jq -r '.status')
  
  case "$STATUS" in
    DOWNLOADED)
      # Verify in Jellyfin
      JELLYFIN=$("$SCRIPT_DIR/check-jellyfin.sh" "$TITLE" "$YEAR" 2>/dev/null || echo '{"status":"NOT_FOUND"}')
      JF_STATUS=$(echo "$JELLYFIN" | jq -r '.status')
      JF_ID=$(echo "$JELLYFIN" | jq -r '.jellyfinId // null')
      QUALITY=$(echo "$DOWNLOAD_STATUS" | jq -r '.quality // "Unknown"')
      
      # Create notification
      NOTIFICATION=$(jq -n \
        --arg event "download_complete" \
        --arg title "$TITLE" \
        --arg year "$YEAR" \
        --arg radarrId "$RADARR_ID" \
        --arg quality "$QUALITY" \
        --arg jfStatus "$JF_STATUS" \
        --arg jfId "$JF_ID" \
        --arg by "$REQUESTED_BY" \
        --arg session "$REPLY_SESSION" \
        '{
          event: $event,
          title: $title,
          year: ($year | tonumber),
          radarrId: ($radarrId | tonumber),
          quality: $quality,
          jellyfinStatus: $jfStatus,
          jellyfinId: $jfId,
          message: "\($title) (\($year)) is ready to watch! 🍿",
          requestedBy: $by,
          replySession: $session
        }')
      
      echo "$NOTIFICATION"
      
      # Write to notification file
      echo "$NOTIFICATION" >> "$NOTIFY_FILE"
      
      # Send to Magi via MQTT if replySession is magi
      if [ "$REPLY_SESSION" = "magi" ] || [ "$REPLY_SESSION" = "magi-family" ]; then
        "$SCRIPT_DIR/notify-magi.sh" "$NOTIFICATION" 2>/dev/null || true
      fi
      
      # Remove from pending
      UPDATED_PENDING=$(echo "$UPDATED_PENDING" | jq --arg id "$RADARR_ID" 'del(.[$id])')
      ;;
      
    DOWNLOADING)
      # Still in progress, keep in pending
      ;;
      
    SEARCHING)
      # Still searching, keep in pending
      ;;
      
    *)
      # Unknown status or error, keep in pending for now
      ;;
  esac
done

# Save updated pending
echo "$UPDATED_PENDING" > "$PENDING_FILE"
