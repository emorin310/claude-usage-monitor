#!/bin/bash
# recover-marvin.sh - Attempt to recover Marvin from crash/bloat
# Called automatically by check-marvin-health.sh or manually

MARVIN_HOST="marvin@marvinbot"
MARVIN_CONFIG_DIR="/home/marvin/.moltbot"
MARVIN_SESSIONS_DIR="$MARVIN_CONFIG_DIR/sessions"
DISCORD_USER_ID="793158038881042434"
SCRIPT_DIR="$(dirname "$0")"

timestamp=$(date "+%Y-%m-%d %H:%M:%S")
echo "[$timestamp] 🔧 Starting Marvin recovery..."

# Step 1: Check if SSH is reachable
if ! ssh -o ConnectTimeout=5 "$MARVIN_HOST" "echo ok" &>/dev/null; then
    echo "[$timestamp] ❌ Cannot SSH to Marvin - host unreachable"
    echo "[$timestamp] 📱 Alerting Eric..."
    # Alert via Telegram if available
    exit 1
fi

echo "[$timestamp] ✅ SSH connection OK"

# Step 2: Stop gateway
echo "[$timestamp] Stopping gateway..."
ssh "$MARVIN_HOST" "systemctl --user stop clawdbot-gateway" 2>/dev/null

# Step 3: Check for bloated sessions
echo "[$timestamp] Checking for bloated sessions..."
bloated_count=$(ssh "$MARVIN_HOST" "find $MARVIN_SESSIONS_DIR -name '*.jsonl' -size +100k 2>/dev/null | wc -l")

if [[ "$bloated_count" -gt 0 ]]; then
    echo "[$timestamp] Found $bloated_count bloated session files, stashing..."
    ssh "$MARVIN_HOST" "mkdir -p $MARVIN_SESSIONS_DIR/stashed && find $MARVIN_SESSIONS_DIR -maxdepth 1 -name '*.jsonl' -size +100k -exec mv {} $MARVIN_SESSIONS_DIR/stashed/ \;"
fi

# Step 4: Clear model overrides from sessions.json
echo "[$timestamp] Clearing model overrides..."
ssh "$MARVIN_HOST" "cd $MARVIN_CONFIG_DIR && if [ -f sessions.json ]; then jq 'walk(if type == \"object\" then del(.modelOverride, .providerOverride) else . end)' sessions.json > sessions.json.tmp && mv sessions.json.tmp sessions.json; fi" 2>/dev/null

# Step 5: Restart gateway
echo "[$timestamp] Restarting gateway..."
ssh "$MARVIN_HOST" "systemctl --user start clawdbot-gateway"

# Step 6: Wait and verify
sleep 5
health=$(ssh "$MARVIN_HOST" "curl -s --max-time 5 http://localhost:18789/health" 2>/dev/null)

if [[ -n "$health" ]]; then
    echo "[$timestamp] ✅ Marvin recovered successfully!"
    # Reset failure counter
    echo '{"consecutiveFailures": 0, "lastCheck": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'", "lastStatus": "recovered"}' > "$HOME/clawd/memory/marvin-health-state.json"
    
    # Post to Council
    curl -s -X POST "https://api.todoist.com/rest/v2/comments" \
        -H "Authorization: Bearer 1425e4eff8e83fc361d6bdd4ac9922c34d5089db" \
        -H "Content-Type: application/json" \
        -d "{\"task_id\": \"9960450404\", \"content\": \"🤖 **[AUTO-RECOVERY] Marvin recovered by Magi**\n\nTimestamp: $timestamp\nBloated sessions stashed: $bloated_count\nStatus: ✅ Gateway healthy\n\n- Magi (automated)\"}" >/dev/null
else
    echo "[$timestamp] ❌ Recovery failed - Marvin still unhealthy"
    echo "[$timestamp] 📱 Alerting Eric..."
    # Could add Telegram notification here
fi
