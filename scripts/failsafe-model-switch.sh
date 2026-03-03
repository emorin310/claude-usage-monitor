#!/bin/bash
# Magi Failsafe: Auto-switch to free model if quota exceeded

LOG_FILE="/Users/eric/clawd/logs/failsafe.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Test if Magi can respond (send a simple status check)
RESPONSE=$(clawdbot session send --session main --message "HEALTH_CHECK" --timeout 10 2>&1)

if [[ $? -ne 0 ]] || [[ "$RESPONSE" =~ "quota" ]] || [[ "$RESPONSE" =~ "rate limit" ]] || [[ "$RESPONSE" =~ "exceeded" ]]; then
    echo "[$TIMESTAMP] ⚠️ Magi unresponsive or quota error detected. Switching to Gemini Flash..." >> "$LOG_FILE"
    
    # Switch to free model
    clawdbot session model --session main --model google/gemini-2.0-flash-exp >> "$LOG_FILE" 2>&1
    
    # Notify Eric via Discord (using OpenClaw message)
    openclaw message send --channel discord --target emorin310 \
        --message "🚨 **Failsafe Triggered**

Magi hit quota limits and auto-switched to Gemini Flash (free tier).

Reduced capabilities but still operational! 🤖" >> "$LOG_FILE" 2>&1
    
    echo "[$TIMESTAMP] ✅ Switched to Gemini Flash and notified Eric" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] ✓ Magi healthy" >> "$LOG_FILE"
fi
