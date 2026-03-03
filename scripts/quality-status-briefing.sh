#!/bin/bash
# quality-status-briefing.sh - Generate quality upgrade status for daily briefings
# Usage: ./quality-status-briefing.sh [--format json|text]

set -e

WORKSPACE="/home/magi/clawd"
DB_PATH="$WORKSPACE/memory/database/memory.db"
STATE_FILE="$WORKSPACE/memory/quality-upgrade-state.json"
FORMAT="${1:-text}"

# Get queue status from database
get_queue_status() {
    if command -v node >/dev/null; then
        cd "$WORKSPACE/scripts" && node -e "
            const Database = require('node:sqlite').DatabaseSync || require('better-sqlite3');
            const db = new Database('$DB_PATH');
            
            const queued = db.prepare('SELECT COUNT(*) as count FROM quality_queue WHERE status = ?').get('queued');
            const inProgress = db.prepare('SELECT COUNT(*) as count FROM quality_queue WHERE status = ?').get('in_progress');
            const completed = db.prepare('SELECT COUNT(*) as count FROM quality_queue WHERE status = ?').get('completed');
            const total = db.prepare('SELECT COUNT(*) as count FROM quality_queue').get();
            
            const nextItem = db.prepare(\`SELECT title, year, priority, current_quality FROM quality_queue WHERE status = ? ORDER BY 
                CASE 
                    WHEN priority LIKE '%HIGH%' THEN 1
                    WHEN priority LIKE '%MEDIUM%' THEN 2 
                    WHEN priority LIKE '%LOW%' THEN 3
                    ELSE 4
                END, id ASC LIMIT 1\`).get('queued');
            
            console.log(JSON.stringify({
                queued: queued.count,
                in_progress: inProgress.count,
                completed: completed.count,
                total: total.count,
                next_item: nextItem
            }));
            
            db.close();
        " 2>/dev/null || echo '{"error": "database_access_failed"}'
    else
        echo '{"error": "node_not_available"}'
    fi
}

# Get daily state info
get_daily_state() {
    if [[ -f "$STATE_FILE" ]]; then
        TODAY=$(date '+%Y-%m-%d')
        TODAY_COUNT=$(jq -r ".daily_requests.\"$TODAY\" // 0" "$STATE_FILE" 2>/dev/null || echo "0")
        TOTAL_PROCESSED=$(jq -r '.total_processed // 0' "$STATE_FILE" 2>/dev/null || echo "0")
        LAST_PROCESSED=$(jq -r '.last_processed // null' "$STATE_FILE" 2>/dev/null || echo "null")
    else
        TODAY_COUNT=0
        TOTAL_PROCESSED=0
        LAST_PROCESSED="null"
    fi
    
    echo "{\"today_count\": $TODAY_COUNT, \"total_processed\": $TOTAL_PROCESSED, \"last_processed\": $LAST_PROCESSED}"
}

# Main execution
QUEUE_STATUS=$(get_queue_status)
DAILY_STATE=$(get_daily_state)

if [[ "$FORMAT" == "json" ]]; then
    jq -n --argjson queue "$QUEUE_STATUS" --argjson daily "$DAILY_STATE" '{
        queue_status: $queue,
        daily_state: $daily,
        rate_limit: {max_per_day: 1, remaining: (1 - $daily.today_count)},
        timestamp: now
    }'
else
    # Text format for Discord briefings
    QUEUED=$(echo "$QUEUE_STATUS" | jq -r '.queued // 0')
    IN_PROGRESS=$(echo "$QUEUE_STATUS" | jq -r '.in_progress // 0') 
    COMPLETED=$(echo "$QUEUE_STATUS" | jq -r '.completed // 0')
    TOTAL=$(echo "$QUEUE_STATUS" | jq -r '.total // 0')
    
    TODAY_COUNT=$(echo "$DAILY_STATE" | jq -r '.today_count // 0')
    REMAINING=$((1 - TODAY_COUNT))
    
    if [[ "$TOTAL" -eq 0 ]]; then
        echo "📺 **Quality Upgrades:** No movies in queue"
    else
        echo "📺 **Quality Upgrades:** $QUEUED queued, $IN_PROGRESS in progress, $COMPLETED completed ($TOTAL total)"
        echo "   📊 Today: $TODAY_COUNT/1 requests sent, $REMAINING remaining"
        
        if [[ "$QUEUED" -gt 0 ]]; then
            NEXT_TITLE=$(echo "$QUEUE_STATUS" | jq -r '.next_item.title // "Unknown"')
            NEXT_YEAR=$(echo "$QUEUE_STATUS" | jq -r '.next_item.year // "Unknown"')
            NEXT_QUALITY=$(echo "$QUEUE_STATUS" | jq -r '.next_item.current_quality // "Unknown"')
            NEXT_PRIORITY=$(echo "$QUEUE_STATUS" | jq -r '.next_item.priority // "Unknown"')
            
            if [[ "$REMAINING" -gt 0 ]]; then
                echo "   🎯 Next: $NEXT_TITLE ($NEXT_YEAR) - $NEXT_QUALITY [$NEXT_PRIORITY]"
            else
                echo "   ⏸️  Rate limited - Next: $NEXT_TITLE ($NEXT_YEAR) tomorrow"
            fi
        fi
    fi
fi