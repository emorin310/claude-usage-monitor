#!/bin/bash
# Jellyfin Quick Connect Authorization
# Usage: ./quickconnect.sh <code>

JELLYFIN_URL="http://192.168.1.96:8096"
JELLYFIN_API_KEY="${JELLYFIN_API_KEY:-$(cat ~/clawd/secrets/jellyfin-api-key 2>/dev/null)}"

if [ -z "$1" ]; then
    echo "Usage: $0 <quick-connect-code>"
    echo "Example: $0 ABC123"
    exit 1
fi

CODE="$1"

# Check if Quick Connect is enabled
ENABLED=$(curl -s "${JELLYFIN_URL}/QuickConnect/Enabled")
if [ "$ENABLED" != "true" ]; then
    echo "❌ Quick Connect is not enabled on this Jellyfin server"
    exit 1
fi

# Authorize the code
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    "${JELLYFIN_URL}/QuickConnect/Authorize?Code=${CODE}&UserId=" \
    -H "X-Emby-Token: ${JELLYFIN_API_KEY}" \
    -H "Content-Type: application/json")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "204" ]; then
    echo "✅ Quick Connect code '${CODE}' authorized successfully!"
    echo "The device should now be logged in."
else
    echo "❌ Failed to authorize code '${CODE}'"
    echo "HTTP Status: $HTTP_CODE"
    echo "Response: $BODY"
    exit 1
fi
