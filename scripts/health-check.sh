#!/bin/bash
# Background health checks - runs every 30 minutes during waking hours

set -e

LOG_FILE="/home/magi/clawd/logs/health-check.log"
STATE_FILE="/home/magi/clawd/memory/health-check-state.json"

mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$STATE_FILE")"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Initialize state file if it doesn't exist
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << 'EOF'
{
  "lastChecks": {
    "email": null,
    "calendar": null,
    "services": null
  },
  "lastAlerts": {
    "email": null,
    "calendar": null,
    "services": null
  }
}
EOF
fi

# Check if it's waking hours (7am-11pm EST)
CURRENT_HOUR=$(date '+%H')
if [ "$CURRENT_HOUR" -lt 7 ] || [ "$CURRENT_HOUR" -ge 23 ]; then
    log "Outside waking hours ($CURRENT_HOUR:xx), skipping health check"
    exit 0
fi

log "Starting health check..."

# Create alerts array
ALERTS=()

# Health check functions will be called by the main Magi agent via cron
# This script serves as a coordinator and state tracker

# Update state file with current check time
CURRENT_TIME=$(date '+%s')
jq ".lastChecks.health = $CURRENT_TIME" "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"

# If we have alerts, they'll be handled by the main agent
if [ ${#ALERTS[@]} -gt 0 ]; then
    log "Health check found issues - will be handled by main agent"
else
    log "Health check completed - no issues found"
fi

# The actual health checking logic will be in the main Magi cron job
# This script is just the coordinator
exit 0