#!/bin/zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/.pid"

if [[ -f "$PID_FILE" ]]; then
  kill "$(cat "$PID_FILE")" 2>/dev/null && echo "Stopped." || echo "Process not running."
  rm -f "$PID_FILE"
else
  echo "No PID file found. Trying port 3847…"
  lsof -ti :3847 | xargs kill 2>/dev/null && echo "Stopped." || echo "Nothing running on 3847."
fi
