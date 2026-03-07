#!/bin/zsh
# Claude Usage Monitor — Install as macOS LaunchAgent
# Runs automatically on login at http://localhost:3847

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_LABEL="com.claude-usage-monitor"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
NODE="$(which node 2>/dev/null || echo /opt/homebrew/bin/node)"

if [[ ! -x "$NODE" ]]; then
  echo "Error: Node.js not found. Install via: brew install node"
  exit 1
fi

# Install npm dependencies if needed
if [[ ! -d "$SCRIPT_DIR/node_modules" ]]; then
  echo "Installing dependencies..."
  cd "$SCRIPT_DIR" && "$NODE" "$(dirname "$NODE")/../lib/node_modules/npm/bin/npm-cli.js" install
fi

# Write the plist
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_LABEL}</string>

  <key>ProgramArguments</key>
  <array>
    <string>${NODE}</string>
    <string>${SCRIPT_DIR}/server.js</string>
  </array>

  <key>WorkingDirectory</key>
  <string>${SCRIPT_DIR}</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key>
    <string>${HOME}</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <dict>
    <key>SuccessfulExit</key>
    <false/>
  </dict>

  <key>StandardOutPath</key>
  <string>${SCRIPT_DIR}/logs/server.log</string>

  <key>StandardErrorPath</key>
  <string>${SCRIPT_DIR}/logs/server.log</string>

  <key>ThrottleInterval</key>
  <integer>10</integer>
</dict>
</plist>
EOF

mkdir -p "$SCRIPT_DIR/logs"

# Load it now
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load -w "$PLIST_PATH"

sleep 1
echo ""
echo "✓ Claude Usage Monitor installed and running."
echo "  Dashboard: http://localhost:3847"
echo "  Logs:      ${SCRIPT_DIR}/logs/server.log"
echo "  Auto-starts on login."
echo ""
echo "  To open the dashboard now:"
echo "  open http://localhost:3847"
open "http://localhost:3847"
