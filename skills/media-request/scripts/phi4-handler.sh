#!/bin/bash
# phi4-handler.sh - Handle freestyle MQTT requests with local phi4
# Usage: ./phi4-handler.sh '{"from":"magi","payload":{"action":"task","description":"..."}}'
# Returns JSON response

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"

INPUT="$1"
if [ -z "$INPUT" ]; then
  echo '{"status":"ERROR","message":"No input provided"}'
  exit 1
fi

# Extract the message/request
FROM=$(echo "$INPUT" | jq -r '.from // "unknown"')
PAYLOAD=$(echo "$INPUT" | jq -r '.payload // empty')
ACTION=$(echo "$PAYLOAD" | jq -r '.action // empty')
DESCRIPTION=$(echo "$PAYLOAD" | jq -r '.description // .message // .query // empty')

# Build prompt for phi4
SYSTEM_PROMPT='You are Marvin, a home media server assistant. You help with:
- Movie/TV requests (use Radarr/Sonarr)
- Jellyfin library searches
- Quick Connect authorization
- Library statistics

Available shell scripts you can suggest:
- request-movie.sh "title" [year] - Add movie to Radarr
- search-library.sh "query" [movie|tv|all] - Search Jellyfin
- library-stats.sh - Get library counts
- check-download.sh <radarrId> - Check download status
- jellyfin-quickconnect.sh <code> - Authorize Quick Connect

Respond with JSON: {"response":"your message","action":"script_name if needed","args":["arg1","arg2"]}'

USER_PROMPT="Request from $FROM:
Action: $ACTION
Details: $DESCRIPTION

What should I do? Respond with JSON only."

# Call phi4
RESPONSE=$(curl -s -m 180 "$OLLAMA_URL/api/generate" \
  -d "$(jq -n \
    --arg model "phi4:latest" \
    --arg system "$SYSTEM_PROMPT" \
    --arg prompt "$USER_PROMPT" \
    '{model: $model, system: $system, prompt: $prompt, stream: false}')" \
  | jq -r '.response // empty')

if [ -z "$RESPONSE" ]; then
  echo '{"status":"ERROR","message":"phi4 did not respond"}'
  exit 1
fi

# Try to parse as JSON, otherwise wrap it
if echo "$RESPONSE" | jq . >/dev/null 2>&1; then
  # Valid JSON - check if we should execute an action
  SUGGESTED_ACTION=$(echo "$RESPONSE" | jq -r '.action // empty')
  ARGS=$(echo "$RESPONSE" | jq -r '.args // [] | @json')
  
  if [ -n "$SUGGESTED_ACTION" ] && [ -f "$SCRIPT_DIR/$SUGGESTED_ACTION" ]; then
    # Execute the suggested script
    SCRIPT_RESULT=$("$SCRIPT_DIR/$SUGGESTED_ACTION" $(echo "$ARGS" | jq -r '.[]') 2>&1)
    echo "$RESPONSE" | jq --arg result "$SCRIPT_RESULT" '. + {executed: true, scriptResult: $result}'
  else
    echo "$RESPONSE"
  fi
else
  # Not JSON, wrap the response
  echo "{\"status\":\"OK\",\"response\":$(echo "$RESPONSE" | jq -Rs .)}"
fi
