#!/bin/bash
# weekly-maintenance.sh - Weekly token optimization maintenance
# Add to cron: 0 9 * * 1 ~/clawd/scripts/weekly-maintenance.sh

echo "🔧 Weekly OpenClaw Maintenance - $(date)"
echo "═══════════════════════════════════════════════════"

# 1. File size monitoring
echo "📊 Checking file sizes..."
~/clawd/scripts/file-size-monitor.sh

echo ""

# 2. Session status check
echo "💰 Current session status:"
openclaw agent status || echo "⚠️ Could not fetch session status"

echo ""

# 3. Memory cleanup suggestions
echo "🧹 Memory optimization suggestions:"
MEMORY_SIZE=$(find ~/clawd/memory -name "*.md" -exec cat {} \; 2>/dev/null | wc -c)
MEMORY_FILES=$(find ~/clawd/memory -name "*.md" 2>/dev/null | wc -l)

echo "   Memory files: $MEMORY_FILES files, $(($MEMORY_SIZE / 1024))KB total"

if [ "$MEMORY_SIZE" -gt 51200 ]; then  # >50KB
    echo "   💡 Consider archiving old memory files"
    find ~/clawd/memory -name "*.md" -mtime +30 2>/dev/null | head -5 | while read -r file; do
        echo "      - Archive: $(basename "$file")"
    done
fi

echo ""

# 4. Model usage efficiency check
echo "🎯 Model strategy compliance:"
if [ -f ~/clawd/MODEL-STRATEGY.md ]; then
    echo "   ✅ Model strategy documented"
else
    echo "   ⚠️ Model strategy missing"
fi

if [ -f ~/clawd/TOKEN-OPTIMIZATION.md ]; then
    echo "   ✅ Token optimization guide available"
else
    echo "   ⚠️ Token optimization guide missing"
fi

echo ""
echo "🎯 Maintenance complete! Review any warnings above."
echo "═══════════════════════════════════════════════════"