#!/usr/bin/env bash
# Session Health Check - Prevents context bloat before it happens
# Run this daily via cron to keep sessions clean

set -euo pipefail

SESSIONS_DIR="${HOME}/.clawdbot/agents/main/sessions"
THRESHOLD_MB=5  # Stash sessions larger than this
STALE_DAYS=7    # Stash sessions older than this

echo "🔍 Session Health Check - $(date)"

# Count total sessions
TOTAL=$(find "$SESSIONS_DIR" -name "*.jsonl" 2>/dev/null | wc -l | tr -d ' ')
echo "📊 Total sessions: $TOTAL"

# Find large sessions
echo ""
echo "🔎 Large sessions (>${THRESHOLD_MB}MB):"
LARGE=0
while IFS= read -r file; do
  if [ -f "$file" ]; then
    SIZE=$(du -m "$file" | cut -f1)
    if [ "$SIZE" -gt "$THRESHOLD_MB" ]; then
      BASENAME=$(basename "$file")
      echo "  ⚠️  $BASENAME - ${SIZE}MB"
      LARGE=$((LARGE + 1))
    fi
  fi
done < <(find "$SESSIONS_DIR" -name "*.jsonl" 2>/dev/null)

# Find stale sessions
echo ""
echo "🕰️  Stale sessions (>${STALE_DAYS} days old):"
STALE=0
while IFS= read -r file; do
  if [ -f "$file" ]; then
    BASENAME=$(basename "$file")
    echo "  📅 $BASENAME"
    STALE=$((STALE + 1))
  fi
done < <(find "$SESSIONS_DIR" -name "*.jsonl" -mtime +${STALE_DAYS} 2>/dev/null)

# Summary
echo ""
echo "📈 Summary:"
echo "  - Total sessions: $TOTAL"
echo "  - Large (>${THRESHOLD_MB}MB): $LARGE"
echo "  - Stale (>${STALE_DAYS}d): $STALE"

# Recommend action
if [ "$LARGE" -gt 10 ] || [ "$STALE" -gt 50 ]; then
  echo ""
  echo "⚠️  RECOMMENDED: Run cleanup script to prevent bloat"
  echo "    ~/clawd-magi/scripts/session-cleanup.sh"
fi
