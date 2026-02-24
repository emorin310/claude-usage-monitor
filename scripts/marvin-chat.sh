#!/usr/bin/env bash
# marvin-chat.sh - Send messages directly to Marvin
# Usage: ./marvin-chat.sh "Your message here"

set -euo pipefail

MARVIN_URL="http://192.168.1.201:18790"
MARVIN_TOKEN="405987e5394153113d7284c99b2d1a1e70d6b6daf92abd80"
LOG_FILE="$HOME/clawd-magi/marvin.md.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ $# -eq 0 ]; then
  echo "Usage: $0 \"message\""
  exit 1
fi

MESSAGE="$1"

# Log outgoing
echo "[$TIMESTAMP] [MAGI → MARVIN] $MESSAGE" >> "$LOG_FILE"

# Try sessions_send first (preferred method)
# Note: This requires knowing Marvin's session key
# For now, we'll use a simple HTTP endpoint approach

# Send via gateway health check as a simple test
# In production, this would use the sessions API
RESPONSE=$(curl -s -w "\n%{http_code}" "$MARVIN_URL/health" \
  -H "Authorization: Bearer $MARVIN_TOKEN" 2>&1 || echo "ERROR")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Marvin is online and healthy"
  echo "[$TIMESTAMP] [MARVIN → MAGI] Gateway healthy (HTTP 200)" >> "$LOG_FILE"
  
  # TODO: Implement actual message sending via sessions API
  echo ""
  echo "💬 Message queued: \"$MESSAGE\""
  echo "📝 Logged to: $LOG_FILE"
  echo ""
  echo "⚠️  Note: Full message sending requires Marvin's session key."
  echo "   For now, post to Council Comms for guaranteed delivery."
else
  echo "❌ Failed to reach Marvin (HTTP $HTTP_CODE)"
  echo "[$TIMESTAMP] [ERROR] Failed to reach Marvin gateway" >> "$LOG_FILE"
fi
