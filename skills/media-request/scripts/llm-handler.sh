#!/bin/bash
# llm-handler.sh - Handle freestyle MQTT requests with DeepSeek (fast, cheap)
# Usage: ./llm-handler.sh '{"from":"magi","payload":{"action":"task","description":"..."}}'
# Returns JSON response

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Gemini Flash - fast, cheap tier 3
GOOGLE_KEY="${GOOGLE_API_KEY:-}"
GEMINI_URL="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

INPUT="$1"
if [ -z "$INPUT" ]; then
  echo '{"status":"ERROR","message":"No input provided"}'
  exit 1
fi

# Check for API key
if [ -z "$GOOGLE_KEY" ]; then
  [ -f ~/.marvin_bootstrap ] && source ~/.marvin_bootstrap 2>/dev/null
  GOOGLE_KEY="${GOOGLE_API_KEY:-}"
fi

if [ -z "$GOOGLE_KEY" ]; then
  echo '{"status":"ERROR","message":"GOOGLE_API_KEY not set"}'
  exit 1
fi

# Extract the message/request
FROM=$(echo "$INPUT" | jq -r '.from // "unknown"')
PAYLOAD=$(echo "$INPUT" | jq -r '.payload // empty')
ACTION=$(echo "$PAYLOAD" | jq -r '.action // empty')
DESCRIPTION=$(echo "$PAYLOAD" | jq -r '.description // .message // .query // empty')

# Build prompt
SYSTEM_PROMPT='You are Marvin, a home media server assistant. Respond with JSON only.
Available actions you can suggest:
- request-movie.sh "title" [year] - Add movie to Radarr
- search-library.sh "query" [movie|tv|all] - Search Jellyfin
- library-stats.sh - Get library counts
- check-download.sh <radarrId> - Check download status

Respond: {"response":"your message","action":"script_name or null","args":["arg1","arg2"]}'

USER_MSG="Request from $FROM - Action: $ACTION - Details: $DESCRIPTION"

# Call Gemini Flash
RESPONSE=$(curl -s -m 30 "${GEMINI_URL}?key=${GOOGLE_KEY}" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg sys "$SYSTEM_PROMPT" \
    --arg user "$USER_MSG" \
    '{
      system_instruction: {parts: [{text: $sys}]},
      contents: [{parts: [{text: $user}]}],
      generationConfig: {maxOutputTokens: 500}
    }')")

# Extract response
CONTENT=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[0].text // empty')

if [ -z "$CONTENT" ]; then
  ERROR=$(echo "$RESPONSE" | jq -r '.error.message // "Unknown error"')
  echo "{\"status\":\"ERROR\",\"message\":\"Gemini: $ERROR\"}"
  exit 1
fi

# Try to parse as JSON and optionally execute
if echo "$CONTENT" | jq . >/dev/null 2>&1; then
  SUGGESTED_ACTION=$(echo "$CONTENT" | jq -r '.action // empty')
  
  if [ -n "$SUGGESTED_ACTION" ] && [ "$SUGGESTED_ACTION" != "null" ] && [ -f "$SCRIPT_DIR/$SUGGESTED_ACTION" ]; then
    ARGS=$(echo "$CONTENT" | jq -r '.args // [] | .[]' | tr '\n' ' ')
    SCRIPT_RESULT=$("$SCRIPT_DIR/$SUGGESTED_ACTION" $ARGS 2>&1)
    echo "$CONTENT" | jq --arg result "$SCRIPT_RESULT" '. + {executed: true, scriptResult: $result}'
  else
    echo "$CONTENT"
  fi
else
  echo "{\"status\":\"OK\",\"response\":$(echo "$CONTENT" | jq -Rs .)}"
fi
