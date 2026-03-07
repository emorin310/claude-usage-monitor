#!/bin/zsh
# Starts Claude Usage Monitor in the background and opens the dashboard

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-3847}"
PID_FILE="$SCRIPT_DIR/.pid"

# Kill any existing instance
if [[ -f "$PID_FILE" ]]; then
  kill "$(cat "$PID_FILE")" 2>/dev/null
  rm -f "$PID_FILE"
fi

# Start server
cd "$SCRIPT_DIR"
/opt/homebrew/bin/node server.js &
echo $! > "$PID_FILE"

sleep 1
echo "Claude Usage Monitor running at http://localhost:${PORT}"
open "http://localhost:${PORT}"
