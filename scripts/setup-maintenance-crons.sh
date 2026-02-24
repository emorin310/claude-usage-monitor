#!/bin/bash
# Setup maintenance cron jobs

set -e

SCRIPT_DIR="/home/magi/clawd/scripts"
LOG_DIR="/home/magi/clawd/logs"

# Make scripts executable
chmod +x "$SCRIPT_DIR/auto-update.sh"
chmod +x "$SCRIPT_DIR/github-backup.sh"
chmod +x "$SCRIPT_DIR/health-check.sh"

# Create logs directory
mkdir -p "$LOG_DIR"

# Backup current crontab
crontab -l > /tmp/current_cron 2>/dev/null || echo "# Empty crontab" > /tmp/current_cron

# Add our cron jobs
cat >> /tmp/current_cron << 'EOF'

# OpenClaw Maintenance Jobs
# Auto-update OpenClaw at 4:00 AM daily
0 4 * * * /home/magi/clawd/scripts/auto-update.sh && echo "$(cat /tmp/update_report.txt)" | openclaw message send --channel discord --target monitoring

# GitHub backup at 4:30 AM daily  
30 4 * * * /home/magi/clawd/scripts/github-backup.sh && echo "$(cat /tmp/backup_report.txt)" | openclaw message send --channel discord --target monitoring

# Health checks every 30 minutes during waking hours (7 AM - 11 PM)
0,30 7-22 * * * openclaw run --model haiku --task "Run health check: 1) Check Gmail for urgent emails (flag payment failures, security alerts, expiring subscriptions, meeting changes, anything needing action today). 2) Check calendar for events in next 2 hours. 3) Only alert if something needs attention - no 'all clear' messages. Use DRAFT-ONLY for emails. Severity: 'urgent' for <1hr, 'heads up' for today." --channel discord --target monitoring

EOF

# Install new crontab
crontab /tmp/current_cron

echo "✅ Maintenance cron jobs installed successfully!"
echo ""
echo "📅 Scheduled jobs:"
echo "   • 4:00 AM - Auto-update OpenClaw"  
echo "   • 4:30 AM - Backup to GitHub"
echo "   • Every 30 min (7 AM - 11 PM) - Health checks"
echo ""
echo "📝 Logs will be saved to: $LOG_DIR/"
echo "📢 Notifications sent to Discord #monitoring"
echo ""
echo "To view current crontab: crontab -l"
echo "To edit crontab: crontab -e"