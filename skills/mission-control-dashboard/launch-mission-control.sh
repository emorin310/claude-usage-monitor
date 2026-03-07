#!/bin/bash
cd "$(dirname "$0")"

echo "🌙 Mega Dark Mission Control Dashboard Launcher"
echo "============================================"

# Kill any existing dashboard processes
echo "🔄 Stopping existing dashboards..."
pkill -f "dashboard.js" 2>/dev/null || true
sleep 2

# Start the mega dark dashboard
echo "🚀 Starting Mega Dark Mission Control..."
nohup node mega-dark-dashboard.js > mission-control.log 2>&1 &
PID=$!

# Wait a moment for startup
sleep 3

# Test if it's running
if ps -p $PID > /dev/null; then
    echo "✅ Dashboard started successfully!"
    echo "📱 URL: http://192.168.1.132:3002"
    echo "🔑 Login: admin / magrathea2024!"
    echo "📊 Features: Agent Fleet, Token Analytics, Mission Board"
    echo "📝 Logs: tail -f mission-control.log"
    echo ""
    echo "🎛️ Mission Control is online! 🚀"
else
    echo "❌ Failed to start dashboard"
    echo "📝 Check logs: cat mission-control.log"
fi
