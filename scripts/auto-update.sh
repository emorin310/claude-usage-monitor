#!/bin/bash
# Auto-update script for OpenClaw - runs at 4:00am daily

set -e

LOG_FILE="/home/magi/clawd/logs/auto-update.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to send Discord notification
notify_discord() {
    local message="$1"
    local urgency="${2:-info}"
    
    # Use openclaw message command to send to monitoring channel
    echo "$message" > /tmp/update_report.txt
    # Will be sent via cron job that calls this script
}

log "Starting OpenClaw auto-update..."

# Store current version for comparison
OLD_VERSION=$(openclaw --version 2>/dev/null || echo "unknown")

# Update OpenClaw
log "Updating OpenClaw package..."
if npm update -g openclaw 2>&1 | tee -a "$LOG_FILE"; then
    log "✅ Package updated successfully"
    UPDATE_SUCCESS=true
else
    log "❌ Package update failed"
    UPDATE_SUCCESS=false
fi

# Get new version
NEW_VERSION=$(openclaw --version 2>/dev/null || echo "unknown")

# Update gateway
if [ "$UPDATE_SUCCESS" = true ]; then
    log "Updating gateway..."
    if openclaw gateway update 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ Gateway updated successfully"
        GATEWAY_SUCCESS=true
    else
        log "❌ Gateway update failed"
        GATEWAY_SUCCESS=false
    fi
else
    GATEWAY_SUCCESS=false
    log "Skipping gateway update due to package update failure"
fi

# Restart gateway service
if [ "$GATEWAY_SUCCESS" = true ]; then
    log "Restarting gateway service..."
    if openclaw gateway restart 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ Gateway restarted successfully"
        RESTART_SUCCESS=true
    else
        log "❌ Gateway restart failed"
        RESTART_SUCCESS=false
    fi
else
    RESTART_SUCCESS=false
    log "Skipping gateway restart due to update failures"
fi

# Generate report
REPORT="🔄 **Auto-Update Report**\n\n"

if [ "$OLD_VERSION" != "$NEW_VERSION" ]; then
    REPORT+="📦 **Package:** $OLD_VERSION → $NEW_VERSION\n"
else
    REPORT+="📦 **Package:** $OLD_VERSION (no change)\n"
fi

if [ "$UPDATE_SUCCESS" = true ]; then
    REPORT+="✅ Package update: Success\n"
else
    REPORT+="❌ Package update: Failed\n"
fi

if [ "$GATEWAY_SUCCESS" = true ]; then
    REPORT+="✅ Gateway update: Success\n"
else
    REPORT+="❌ Gateway update: Failed\n"
fi

if [ "$RESTART_SUCCESS" = true ]; then
    REPORT+="✅ Service restart: Success\n"
else
    REPORT+="❌ Service restart: Failed\n"
fi

REPORT+="📅 Completed: $(date '+%Y-%m-%d %H:%M:%S')"

# Save report for cron job to send
echo -e "$REPORT" > /tmp/update_report.txt

if [ "$UPDATE_SUCCESS" = true ] && [ "$GATEWAY_SUCCESS" = true ] && [ "$RESTART_SUCCESS" = true ]; then
    log "✅ All updates completed successfully"
    exit 0
else
    log "❌ Some updates failed - check log for details"
    exit 1
fi