#!/bin/bash
# process-quality-queue.sh - Automated movie quality upgrade processing
# Rate limited: Max 2 upgrades per day
# Usage: ./process-quality-queue.sh [--dry-run]

set -e

WORKSPACE="/home/magi/clawd"
DB_PATH="$WORKSPACE/memory/database/memory.db"
LOG_PATH="$WORKSPACE/logs/quality-upgrades.log"
STATE_FILE="$WORKSPACE/memory/quality-upgrade-state.json"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_PATH")"

# Check for dry run flag
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_PATH"
}

log "🎬 Quality upgrade processor started (DRY_RUN=$DRY_RUN)"

# Read current state (requests sent today)
if [[ -f "$STATE_FILE" ]]; then
    TODAY_COUNT=$(jq -r ".daily_requests.\"$(date '+%Y-%m-%d')\" // 0" "$STATE_FILE" 2>/dev/null || echo "0")
else
    TODAY_COUNT=0
    echo '{"daily_requests": {}, "last_processed": null, "total_processed": 0}' > "$STATE_FILE"
fi

RATE_LIMIT=1
REMAINING=$((RATE_LIMIT - TODAY_COUNT))

log "📊 Today's requests: $TODAY_COUNT/$RATE_LIMIT (remaining: $REMAINING)"

if [[ "$REMAINING" -le 0 ]]; then
    log "⏸️  Rate limit reached for today. Next processing: tomorrow."
    exit 0
fi

# Get next queued item(s) from database (prioritized order)
QUEUED_ITEMS=$(cd "$WORKSPACE/scripts" && node -e "
const Database = require('node:sqlite').DatabaseSync;
const db = new Database('$DB_PATH');
const items = db.prepare(\`SELECT * FROM quality_queue WHERE status = ? ORDER BY 
    CASE 
        WHEN priority LIKE '%HIGH%' THEN 1
        WHEN priority LIKE '%MEDIUM%' THEN 2 
        WHEN priority LIKE '%LOW%' THEN 3
        ELSE 4
    END, id ASC\`).all('queued');
items.forEach(item => console.log(JSON.stringify(item)));
db.close();
" 2>/dev/null || echo "")

if [[ -z "$QUEUED_ITEMS" ]]; then
    log "📭 No queued items found. Queue is empty."
    exit 0
fi

PROCESSED_COUNT=0
echo "$QUEUED_ITEMS" | head -n "$REMAINING" | while read -r item; do
    if [[ -z "$item" ]]; then
        continue
    fi
    
    TITLE=$(echo "$item" | jq -r '.title')
    YEAR=$(echo "$item" | jq -r '.year')
    ID=$(echo "$item" | jq -r '.id')
    PRIORITY=$(echo "$item" | jq -r '.priority')
    CURRENT_QUALITY=$(echo "$item" | jq -r '.current_quality')
    
    log "🔄 Processing: $TITLE ($YEAR) - $CURRENT_QUALITY [$PRIORITY]"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "   🧪 DRY RUN: Would send upgrade request to Marvin"
    else
        # Send upgrade request to Marvin
        REQUEST_MESSAGE="[REQUEST] Movie Quality Upgrade

**Movie:** $TITLE ($YEAR)  
**Current:** $CURRENT_QUALITY
**Target:** 1080p+ modern codec (x264/x265/AV1), MKV/MP4 container
**Priority:** $PRIORITY
**Queue ID:** $ID

Please search for better quality version via Radarr. Update when available.

Automated quality improvement workflow active."

        # Send to Marvin
        if ~/bin/msg-marvin "$REQUEST_MESSAGE"; then
            log "   ✅ Request sent to Marvin successfully"
            
            # Update database status
            if command -v node >/dev/null; then
                cd "$WORKSPACE/scripts" && node -e "
                    const Database = require('node:sqlite').DatabaseSync || require('better-sqlite3');
                    const db = new Database('$DB_PATH');
                    db.prepare('UPDATE quality_queue SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
                      .run('in_progress', $ID);
                    db.close();
                    console.log('Database updated: ID $ID -> in_progress');
                "
            fi
            
            # Update state file
            jq --arg date "$(date '+%Y-%m-%d')" --argjson count "$((TODAY_COUNT + PROCESSED_COUNT + 1))" \
               '.daily_requests[$date] = $count | .last_processed = now | .total_processed += 1' \
               "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
               
            PROCESSED_COUNT=$((PROCESSED_COUNT + 1))
            log "   📊 State updated: $(($TODAY_COUNT + PROCESSED_COUNT))/$RATE_LIMIT requests today"
            
        else
            log "   ❌ Failed to send request to Marvin"
        fi
    fi
done

if [[ "$PROCESSED_COUNT" -gt 0 ]]; then
    log "🎯 Processed $PROCESSED_COUNT upgrade request(s) today"
else
    log "📋 No new requests processed"
fi

log "✅ Quality upgrade processor completed"