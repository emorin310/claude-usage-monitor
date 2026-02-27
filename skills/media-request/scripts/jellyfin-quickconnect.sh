#!/bin/bash
# jellyfin-quickconnect.sh - Authorize Quick Connect codes
# Usage: ./jellyfin-quickconnect.sh <code> [userId]

set -e

JELLYFIN_URL="${JELLYFIN_URL:-http://192.168.1.96:8096}"
JELLYFIN_KEY="${JELLYFIN_KEY:-c5b4d7fc157b49778470414e5944b0b2}"

CODE="$1"
# Default to first admin user if not specified
USER_ID="${2:-fd009b7235584be9b9b42fdbb576937f}"

if [ -z "$CODE" ]; then
  echo '{"status":"ERROR","message":"Usage: jellyfin-quickconnect.sh <code> [userId]"}'
  exit 1
fi

# Build URL with query parameters
URL="$JELLYFIN_URL/QuickConnect/Authorize?code=$CODE"
[ -n "$USER_ID" ] && URL="$URL&userId=$USER_ID"

# Try POST with query params
RESULT=$(curl -s -w "\n%{http_code}" -X POST "$URL" \
  -H "Authorization: MediaBrowser Token=\"$JELLYFIN_KEY\"" 2>&1)

HTTP_CODE=$(echo "$RESULT" | tail -1)
BODY=$(echo "$RESULT" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
  echo '{"status":"SUCCESS","message":"Quick Connect authorized!","code":"'"$CODE"'"}'
elif [ "$HTTP_CODE" = "400" ]; then
  echo '{"status":"INVALID","message":"Invalid or expired code","code":"'"$CODE"'"}'
elif [ "$HTTP_CODE" = "401" ]; then
  echo '{"status":"UNAUTHORIZED","message":"Not authorized to approve Quick Connect"}'
else
  echo '{"status":"ERROR","httpCode":"'"$HTTP_CODE"'","response":"'"$BODY"'"}'
fi
