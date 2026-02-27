#!/bin/bash
# handle-request.sh - Process a movie request and track for notification
# Usage: ./handle-request.sh '{"action":"request_movie","title":"...","year":...,"requestedBy":"...","replySession":"..."}'
# Returns JSON response

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
PENDING_FILE="$DATA_DIR/pending-requests.json"

# Ensure data dir exists
mkdir -p "$DATA_DIR"

# Initialize pending file if needed
[ -f "$PENDING_FILE" ] || echo '{}' > "$PENDING_FILE"

# Parse input
INPUT="$1"
if [ -z "$INPUT" ]; then
  echo '{"status":"ERROR","message":"No input provided"}'
  exit 1
fi

ACTION=$(echo "$INPUT" | jq -r '.action')
TITLE=$(echo "$INPUT" | jq -r '.title')
YEAR=$(echo "$INPUT" | jq -r '.year // empty')
REQUESTED_BY=$(echo "$INPUT" | jq -r '.requestedBy // "Unknown"')
REPLY_SESSION=$(echo "$INPUT" | jq -r '.replySession // empty')

case "$ACTION" in
  request_movie)
    # Request the movie
    if [ -n "$YEAR" ]; then
      RESULT=$("$SCRIPT_DIR/request-movie.sh" "$TITLE" "$YEAR")
    else
      RESULT=$("$SCRIPT_DIR/request-movie.sh" "$TITLE")
    fi
    
    STATUS=$(echo "$RESULT" | jq -r '.status')
    RADARR_ID=$(echo "$RESULT" | jq -r '.radarrId // empty')
    MOVIE_TITLE=$(echo "$RESULT" | jq -r '.title')
    MOVIE_YEAR=$(echo "$RESULT" | jq -r '.year')
    
    # If added or already monitored, track for notification
    if [ -n "$RADARR_ID" ] && [ -n "$REPLY_SESSION" ]; then
      if [ "$STATUS" = "ADDED" ] || [ "$STATUS" = "MONITORED" ]; then
        # Add to pending requests
        PENDING=$(cat "$PENDING_FILE")
        PENDING=$(echo "$PENDING" | jq --arg id "$RADARR_ID" \
          --arg title "$MOVIE_TITLE" \
          --arg year "$MOVIE_YEAR" \
          --arg by "$REQUESTED_BY" \
          --arg session "$REPLY_SESSION" \
          '.[$id] = {title: $title, year: $year, requestedBy: $by, replySession: $session, timestamp: now}')
        echo "$PENDING" > "$PENDING_FILE"
      fi
    fi
    
    # Build response
    echo "$RESULT" | jq --arg by "$REQUESTED_BY" --arg event "request_received" \
      '. + {event: $event, requestedBy: $by}'
    ;;
    
  check_status)
    RADARR_ID=$(echo "$INPUT" | jq -r '.radarrId')
    "$SCRIPT_DIR/check-download.sh" "$RADARR_ID"
    ;;
    
  check_jellyfin)
    "$SCRIPT_DIR/check-jellyfin.sh" "$TITLE" "$YEAR"
    ;;
    
  search)
    QUERY=$(echo "$INPUT" | jq -r '.query')
    TYPE=$(echo "$INPUT" | jq -r '.type // "all"')
    "$SCRIPT_DIR/search-library.sh" "$QUERY" "$TYPE"
    ;;
    
  stats)
    "$SCRIPT_DIR/library-stats.sh"
    ;;
    
  *)
    echo '{"status":"ERROR","message":"Unknown action: '"$ACTION"'"}'
    exit 1
    ;;
esac
