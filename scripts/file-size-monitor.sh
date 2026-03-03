#!/bin/bash
# file-size-monitor.sh - Monitor core file sizes for token bloat
# Run weekly to catch file size explosions

WORKSPACE="$HOME/clawd"
THRESHOLD_KB=20  # Alert if core files exceed 20KB
LOG_FILE="$WORKSPACE/logs/file-size-monitor.log"

mkdir -p "$WORKSPACE/logs"

echo "📊 File Size Monitor - $(date)" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"

# Core files to monitor
CORE_FILES=(
    "AGENTS.md"
    "SOUL.md" 
    "MEMORY.md"
    "TOOLS.md"
    "HEARTBEAT.md"
    "USER.md"
    "IDENTITY.md"
    "memory/journal.md"
    "memory/council-state.json"
)

ALERTS=0

for file in "${CORE_FILES[@]}"; do
    filepath="$WORKSPACE/$file"
    if [ -f "$filepath" ]; then
        # Get file size in KB
        size_bytes=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null || echo 0)
        size_kb=$((size_bytes / 1024))
        
        printf "%-25s %6dKB" "$file" "$size_kb" | tee -a "$LOG_FILE"
        
        if [ "$size_kb" -gt "$THRESHOLD_KB" ]; then
            echo " ⚠️  BLOAT WARNING" | tee -a "$LOG_FILE"
            ((ALERTS++))
        else
            echo " ✓" | tee -a "$LOG_FILE"
        fi
    else
        printf "%-25s %6s" "$file" "MISSING" | tee -a "$LOG_FILE"
        echo " 📄" | tee -a "$LOG_FILE"
    fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"

if [ "$ALERTS" -gt 0 ]; then
    echo "🚨 $ALERTS file(s) exceed ${THRESHOLD_KB}KB threshold" | tee -a "$LOG_FILE"
    echo "💡 Consider optimizing large files to reduce token consumption" | tee -a "$LOG_FILE"
else
    echo "✅ All core files within size limits" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"

# Optional: Show memory folder summary
echo "📁 Memory folder summary:" | tee -a "$LOG_FILE"
if [ -d "$WORKSPACE/memory" ]; then
    find "$WORKSPACE/memory" -name "*.md" -o -name "*.json" | head -10 | while read -r file; do
        size_bytes=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        size_kb=$((size_bytes / 1024))
        filename=$(basename "$file")
        printf "   %-20s %4dKB\n" "$filename" "$size_kb" | tee -a "$LOG_FILE"
    done
else
    echo "   Memory folder not found" | tee -a "$LOG_FILE"
fi

exit $ALERTS