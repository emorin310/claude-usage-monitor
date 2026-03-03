#!/bin/bash
# check-marvin-health.sh - Monitor Marvin's gateway health
# Run via cron every 30 minutes

MARVIN_HOST="marvin@marvinbot"
MARVIN_GATEWAY="http://localhost:18789"  # Check locally via SSH since LAN bind is wonky
LOG_FILE="$HOME/clawd/memory/marvin-health.log"
ALERT_THRESHOLD=3  # Alert after 3 consecutive failures

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Check gateway health via SSH
health_check() {
    ssh -o ConnectTimeout=5 "$MARVIN_HOST" "curl -s --max-time 5 $MARVIN_GATEWAY/health" 2>/dev/null
}

# Check if response indicates healthy
is_healthy() {
    local response="$1"
    # Gateway returns HTML or JSON when healthy
    [[ -n "$response" ]] && [[ "$response" != *"Connection refused"* ]]
}

# Get failure count from state file
STATE_FILE="$HOME/clawd/memory/marvin-health-state.json"
get_failure_count() {
    if [[ -f "$STATE_FILE" ]]; then
        jq -r '.consecutiveFailures // 0' "$STATE_FILE" 2>/dev/null || echo 0
    else
        echo 0
    fi
}

set_failure_count() {
    local count=$1
    local status=$2
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "{\"consecutiveFailures\": $count, \"lastCheck\": \"$timestamp\", \"lastStatus\": \"$status\"}" > "$STATE_FILE"
}

# Main check
timestamp=$(date "+%Y-%m-%d %H:%M:%S")
response=$(health_check)
failures=$(get_failure_count)

if is_healthy "$response"; then
    echo "[$timestamp] ✅ Marvin healthy" >> "$LOG_FILE"
    set_failure_count 0 "healthy"
else
    failures=$((failures + 1))
    echo "[$timestamp] ❌ Marvin unhealthy (failure #$failures)" >> "$LOG_FILE"
    set_failure_count "$failures" "unhealthy"
    
    if [[ $failures -ge $ALERT_THRESHOLD ]]; then
        echo "[$timestamp] 🚨 ALERT: Marvin down for $failures checks, attempting recovery..." >> "$LOG_FILE"
        # Attempt recovery
        "$HOME/clawd/scripts/recover-marvin.sh" >> "$LOG_FILE" 2>&1
    fi
fi

# Trim log to last 500 lines
tail -500 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
