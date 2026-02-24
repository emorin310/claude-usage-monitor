#!/bin/bash
# Auto-switch between Opus and Sonnet based on Claude usage

STATE_FILE="$HOME/clawd-magi/memory/model-state.json"
USAGE_SCRIPT="$HOME/clawd-magi/scripts/check-claude-usage.sh"

# Get current usage
USAGE_OUTPUT=$($USAGE_SCRIPT)
USAGE=$(echo "$USAGE_OUTPUT" | grep "all_models" | awk '{print $2}' | sed 's/%//g' | sed 's/,//g' | tr -d ' ')

# Read current model from state file
CURRENT_MODEL=$(jq -r '.current_model' "$STATE_FILE" 2>/dev/null || echo "unknown")

# Determine if switch is needed
SHOULD_SWITCH=false
NEW_MODEL=""
REASON=""

if [ "$USAGE" -ge 75 ] && [ "$CURRENT_MODEL" = "opus" ]; then
    SHOULD_SWITCH=true
    NEW_MODEL="sonnet"
    REASON="Usage at ${USAGE}% - crossing 75% threshold"
elif [ "$USAGE" -le 5 ] && [ "$CURRENT_MODEL" = "sonnet" ]; then
    SHOULD_SWITCH=true
    NEW_MODEL="opus"
    REASON="Usage at ${USAGE}% - below 5% threshold"
fi

# Update state file with current stats (always)
jq --arg model "$CURRENT_MODEL" \
   --arg pct "$USAGE" \
   --arg ts "$(date -Iseconds)" \
   --arg reason "Routine check - Usage ${USAGE}%" \
   '.current_model = $model | .all_models_pct = ($pct | tonumber) | .last_check = $ts | .reason = $reason' \
   "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

if [ "$SHOULD_SWITCH" = true ]; then
    echo "🔄 AUTO-SWITCH: $CURRENT_MODEL → $NEW_MODEL ($REASON)"
    
    # Update model in state file
    jq --arg model "$NEW_MODEL" \
       --arg ts "$(date -Iseconds)" \
       --arg reason "$REASON" \
       '.current_model = $model | .last_switch = $ts | .reason = $reason' \
       "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
    
    # Output switch command for the LLM to execute
    if [ "$NEW_MODEL" = "sonnet" ]; then
        MODEL_FULL="anthropic/claude-sonnet-4-5-20250929"
    else
        MODEL_FULL="anthropic/claude-opus-4-5"
    fi
    
    echo "SWITCH_TO:$MODEL_FULL"
    echo "NOTIFY:🔄 Switched to $NEW_MODEL - Usage at ${USAGE}%"
else
    echo "✅ No switch needed. Current: $CURRENT_MODEL, Usage: ${USAGE}%"
fi
