#!/bin/bash
# Inter-bot communication library
# Source this file: source ~/clawd/skills/inter-bot/scripts/inter-bot.sh

INTERBOT_TOKEN="${INTERBOT_TOKEN:-$(cat ~/.openclaw/inter-bot-token 2>/dev/null)}"
INTERBOT_RESPONSE_DIR="/tmp/interbot-responses"

# Bot registry
declare -A INTERBOT_URLS=(
    ["marvin"]="http://192.168.1.201:18789"
    ["magi"]="http://192.168.1.132:18790"
)

# Get sender identity
interbot_self() {
    hostname | sed 's/bot$//'
}

# Send a simple message to another bot
# Usage: send_to_bot <target> "message"
send_to_bot() {
    local target="$1"
    local message="$2"
    local url="${INTERBOT_URLS[$target]}"
    local sender=$(interbot_self)
    
    if [ -z "$url" ]; then
        echo "❌ Unknown target: $target" >&2
        return 1
    fi
    
    local response=$(curl -s -X POST "${url}/hooks/agent" \
        -H "Authorization: Bearer ${INTERBOT_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"[From ${sender}] ${message}\", \"agentId\": \"main\"}")
    
    local run_id=$(echo "$response" | jq -r '.runId // empty')
    
    if [ -n "$run_id" ]; then
        echo "$run_id"
        return 0
    else
        echo "❌ Failed: $response" >&2
        return 1
    fi
}

# Send a threaded message
# Usage: send_threaded <target> "message" <thread-id>
send_threaded() {
    local target="$1"
    local message="$2"
    local thread_id="$3"
    local url="${INTERBOT_URLS[$target]}"
    local sender=$(interbot_self)
    local msg_id=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)
    
    if [ -z "$url" ]; then
        echo "❌ Unknown target: $target" >&2
        return 1
    fi
    
    mkdir -p "$INTERBOT_RESPONSE_DIR"
    
    local self_host=$(hostname -I | awk '{print $1}')
    local self_port=$(grep -o '"port":\s*[0-9]*' ~/.openclaw/openclaw.json | head -1 | grep -o '[0-9]*')
    local callback="http://${self_host}:${self_port}/hooks/agent"
    
    local payload=$(jq -n \
        --arg msg "[From ${sender}] ${message}" \
        --arg sender "$sender" \
        --arg msgId "$msg_id" \
        --arg threadId "$thread_id" \
        --arg callback "$callback" \
        --arg agentId "main" \
        '{
            message: $msg,
            agentId: $agentId,
            metadata: {
                sender: $sender,
                messageId: $msgId,
                threadId: $threadId,
                callbackUrl: $callback,
                timestamp: (now | tostring)
            }
        }')
    
    local response=$(curl -s -X POST "${url}/hooks/agent" \
        -H "Authorization: Bearer ${INTERBOT_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    local run_id=$(echo "$response" | jq -r '.runId // empty')
    
    if [ -n "$run_id" ]; then
        # Store thread info
        echo "{\"threadId\": \"$thread_id\", \"lastMessageId\": \"$msg_id\", \"target\": \"$target\", \"timestamp\": \"$(date -Iseconds)\"}" \
            > "${INTERBOT_RESPONSE_DIR}/thread-${thread_id}.json"
        echo "$run_id"
        return 0
    else
        echo "❌ Failed: $response" >&2
        return 1
    fi
}

# Send a response back via callback
# Usage: send_response <callback-url> <thread-id> "response message"
send_response() {
    local callback_url="$1"
    local thread_id="$2"
    local message="$3"
    local sender=$(interbot_self)
    local msg_id=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)
    
    local payload=$(jq -n \
        --arg msg "[Response from ${sender}] ${message}" \
        --arg sender "$sender" \
        --arg msgId "$msg_id" \
        --arg threadId "$thread_id" \
        --arg agentId "main" \
        '{
            message: $msg,
            agentId: $agentId,
            metadata: {
                sender: $sender,
                messageId: $msgId,
                threadId: $threadId,
                isResponse: true,
                timestamp: (now | tostring)
            }
        }')
    
    local response=$(curl -s -X POST "${callback_url}" \
        -H "Authorization: Bearer ${INTERBOT_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    local run_id=$(echo "$response" | jq -r '.runId // empty')
    
    if [ -n "$run_id" ]; then
        echo "$run_id"
        return 0
    else
        echo "❌ Failed: $response" >&2
        return 1
    fi
}

# List active threads
# Usage: list_threads
list_threads() {
    if [ ! -d "$INTERBOT_RESPONSE_DIR" ]; then
        echo "(no active threads)"
        return
    fi
    
    for f in "$INTERBOT_RESPONSE_DIR"/thread-*.json; do
        [ -f "$f" ] || continue
        local thread=$(basename "$f" .json | sed 's/thread-//')
        local target=$(jq -r '.target' "$f")
        local time=$(jq -r '.timestamp' "$f")
        echo "$thread → $target (last: $time)"
    done
}
