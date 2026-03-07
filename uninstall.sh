#!/bin/zsh
# Claude Usage Monitor — Uninstall LaunchAgent

PLIST_LABEL="com.claude-usage-monitor"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"

if [[ -f "$PLIST_PATH" ]]; then
  launchctl unload "$PLIST_PATH" 2>/dev/null || true
  rm -f "$PLIST_PATH"
  echo "✓ Claude Usage Monitor uninstalled and stopped."
else
  echo "Not installed as a LaunchAgent (plist not found)."
fi
