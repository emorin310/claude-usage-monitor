#!/usr/bin/env bash
# Session Cleanup - Proactive context bloat prevention
# Safe to run anytime - only stashes old/large sessions

set -euo pipefail

SESSIONS_DIR="${HOME}/.clawdbot/agents/main/sessions"
THRESHOLD_MB=5
STALE_DAYS=7
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "🧹 Session Cleanup - $(date)"
echo ""

# Stash large sessions
echo "📦 Stashing large sessions (>${THRESHOLD_MB}MB)..."
LARGE_COUNT=0
while IFS= read -r file; do
  if [ -f "$file" ]; then
    SIZE=$(du -m "$file" | cut -f1)
    if [ "$SIZE" -gt "$THRESHOLD_MB" ]; then
      BASENAME=$(basename "$file")
      mv "$file" "${file}.large-${TIMESTAMP}"
      echo "  ✓ Stashed: $BASENAME (${SIZE}MB)"
      LARGE_COUNT=$((LARGE_COUNT + 1))
    fi
  fi
done < <(find "$SESSIONS_DIR" -name "*.jsonl" 2>/dev/null)

# Stash stale sessions
echo ""
echo "📦 Stashing stale sessions (>${STALE_DAYS} days old)..."
STALE_COUNT=0
while IFS= read -r file; do
  if [ -f "$file" ]; then
    BASENAME=$(basename "$file")
    mv "$file" "${file}.stale-${TIMESTAMP}"
    echo "  ✓ Stashed: $BASENAME"
    STALE_COUNT=$((STALE_COUNT + 1))
  fi
done < <(find "$SESSIONS_DIR" -name "*.jsonl" -mtime +${STALE_DAYS} 2>/dev/null)

# Clear session overrides
echo ""
echo "🔧 Clearing session overrides..."
cd "${HOME}/.clawdbot/agents/main"
if [ -f sessions.json ]; then
  jq 'walk(if type == "object" then 
    if has("modelOverride") then .modelOverride = null else . end |
    if has("providerOverride") then .providerOverride = null else . end |
    if has("contextTokens") then .contextTokens = 0 else . end
  else . end)' sessions.json > sessions.json.tmp && mv sessions.json.tmp sessions.json
  echo "  ✓ Session overrides cleared"
fi

echo ""
echo "✅ Cleanup complete!"
echo "  - Large sessions stashed: $LARGE_COUNT"
echo "  - Stale sessions stashed: $STALE_COUNT"
echo ""
echo "💡 Tip: Set up a daily cron job to run this automatically:"
echo "   0 3 * * * $HOME/clawd/scripts/session-cleanup.sh"
