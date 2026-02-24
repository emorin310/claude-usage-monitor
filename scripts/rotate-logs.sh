#!/bin/bash
# Log rotation script - runs daily to archive logs by date
# Usage: ./rotate-logs.sh (add to cron for daily execution)

LOG_DIR="$HOME/clawd-magi"
ARCHIVE_DIR="$HOME/clawd-magi/logs/archive"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

# Create archive directory if needed
mkdir -p "$ARCHIVE_DIR"

# Logs to rotate
LOGS=(
    "marvin.md.log"
    "incoming-messages.jsonl"
)

for LOG in "${LOGS[@]}"; do
    LOG_PATH="$LOG_DIR/$LOG"
    
    if [ -f "$LOG_PATH" ] && [ -s "$LOG_PATH" ]; then
        # Get the base name without extension
        BASE_NAME="${LOG%.*}"
        EXT="${LOG##*.}"
        
        # Archive with yesterday's date (since we're rotating at start of new day)
        ARCHIVE_NAME="${BASE_NAME}-${YESTERDAY}.${EXT}"
        ARCHIVE_PATH="$ARCHIVE_DIR/$ARCHIVE_NAME"
        
        # Move current log to archive
        mv "$LOG_PATH" "$ARCHIVE_PATH"
        echo "$(date '+%Y-%m-%d %H:%M:%S') Archived: $LOG -> $ARCHIVE_NAME"
        
        # Create fresh empty log
        touch "$LOG_PATH"
        echo "# Log started: $TODAY" > "$LOG_PATH"
    fi
done

# Clean up archives older than 30 days
find "$ARCHIVE_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null
find "$ARCHIVE_DIR" -name "*.jsonl" -mtime +30 -delete 2>/dev/null

echo "Log rotation complete: $(date)"
