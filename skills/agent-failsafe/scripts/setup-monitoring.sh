#!/bin/bash
# Setup Agent Failsafe Monitoring
# Installs cron jobs and systemd services for continuous monitoring

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SETUP: $*"
}

# Make all scripts executable
make_scripts_executable() {
    log "Making failsafe scripts executable..."
    chmod +x "$SCRIPT_DIR"/*.sh
    log "✅ Scripts are now executable"
}

# Setup health monitoring cron job
setup_health_monitoring_cron() {
    log "Setting up health monitoring cron job..."
    
    # Health check every 5 minutes
    local health_cron="*/5 * * * * $SCRIPT_DIR/health-monitor.sh monitor magi >/dev/null 2>&1"
    
    # Remove existing entries first
    crontab -l 2>/dev/null | grep -v "health-monitor.sh" | crontab - 2>/dev/null || true
    
    # Add new entry
    (crontab -l 2>/dev/null || true; echo "$health_cron") | crontab -
    
    log "✅ Health monitoring cron job installed"
}

# Setup cross-agent monitoring cron job  
setup_cross_agent_monitoring_cron() {
    log "Setting up cross-agent monitoring cron job..."
    
    # Monitor Marvin every 5 minutes (offset by 2 minutes from health check)
    local cross_agent_cron="2-59/5 * * * * $SCRIPT_DIR/cross-agent-reset.sh --monitor marvin 18789 >/dev/null 2>&1"
    
    # Remove existing entries first
    crontab -l 2>/dev/null | grep -v "cross-agent-reset.sh" | crontab - 2>/dev/null || true
    
    # Add new entry
    (crontab -l 2>/dev/null || true; echo "$cross_agent_cron") | crontab -
    
    log "✅ Cross-agent monitoring cron job installed"
}

# Create systemd service for emergency monitoring
create_emergency_service() {
    log "Creating emergency monitoring systemd service..."
    
    local service_file="$HOME/.config/systemd/user/openclaw-emergency-monitor.service"
    local timer_file="$HOME/.config/systemd/user/openclaw-emergency-monitor.timer"
    
    # Create systemd user directory
    mkdir -p "$HOME/.config/systemd/user"
    
    # Create service file
    cat > "$service_file" << EOF
[Unit]
Description=OpenClaw Emergency Health Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=$SCRIPT_DIR/health-monitor.sh monitor magi
User=$(whoami)
WorkingDirectory=$HOME/clawd

# Restart on failure
Restart=on-failure
RestartSec=30

# Environment
Environment=HOME=$HOME
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
EOF
    
    # Create timer file (every 5 minutes)
    cat > "$timer_file" << EOF
[Unit]
Description=Run OpenClaw Emergency Monitor every 5 minutes
Requires=openclaw-emergency-monitor.service

[Timer]
OnCalendar=*:0/5
Persistent=true
AccuracySec=30s

[Install]
WantedBy=timers.target
EOF
    
    # Enable and start the timer
    systemctl --user daemon-reload
    systemctl --user enable openclaw-emergency-monitor.timer
    systemctl --user start openclaw-emergency-monitor.timer
    
    log "✅ Emergency monitoring systemd service created and started"
}

# Setup log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    local logrotate_config="/tmp/openclaw-failsafe-logrotate"
    
    cat > "$logrotate_config" << EOF
$HOME/.openclaw/logs/agent-*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 $(whoami) $(whoami)
}
EOF
    
    # Add to user crontab for log rotation (daily at 2 AM)
    local logrotate_cron="0 2 * * * /usr/sbin/logrotate $logrotate_config >/dev/null 2>&1"
    
    # Remove existing logrotate entries
    crontab -l 2>/dev/null | grep -v "logrotate.*openclaw" | crontab - 2>/dev/null || true
    
    # Add new entry
    (crontab -l 2>/dev/null || true; echo "$logrotate_cron") | crontab -
    
    log "✅ Log rotation configured"
}

# Create emergency reset alias
create_emergency_alias() {
    log "Creating emergency reset aliases..."
    
    local alias_file="$HOME/.openclaw/aliases.sh"
    
    cat > "$alias_file" << EOF
#!/bin/bash
# OpenClaw Failsafe Aliases

# Emergency reset commands
alias magi-reset="$SCRIPT_DIR/failsafe-controller.sh --emergency-reset magi"
alias magi-check="$SCRIPT_DIR/health-monitor.sh check magi"
alias magi-status="$SCRIPT_DIR/health-monitor.sh check-all"

# Cross-agent commands  
alias reset-marvin="$SCRIPT_DIR/cross-agent-reset.sh --reset-other marvin emergency"
alias monitor-marvin="$SCRIPT_DIR/cross-agent-reset.sh --monitor marvin 18789"

# Convenient shortcuts
alias failsafe-status="systemctl --user status openclaw-emergency-monitor.timer"
alias failsafe-logs="tail -f $HOME/.openclaw/logs/agent-*.log"

echo "OpenClaw Failsafe aliases loaded:"
echo "  magi-reset    - Emergency reset Magi"
echo "  magi-check    - Check Magi health"  
echo "  magi-status   - Check all agents"
echo "  reset-marvin  - Request Marvin reset"
echo "  failsafe-logs - View failsafe logs"
EOF

    # Make it executable
    chmod +x "$alias_file"
    
    # Add source command to bashrc if not already present
    if ! grep -q "openclaw/aliases.sh" "$HOME/.bashrc" 2>/dev/null; then
        echo "" >> "$HOME/.bashrc"
        echo "# OpenClaw Failsafe Aliases" >> "$HOME/.bashrc"
        echo "source $alias_file" >> "$HOME/.bashrc"
        log "✅ Emergency aliases added to .bashrc"
    else
        log "✅ Emergency aliases already in .bashrc"
    fi
}

# Test the monitoring system
test_monitoring_system() {
    log "Testing monitoring system..."
    
    # Test health check
    if "$SCRIPT_DIR/health-monitor.sh" check magi; then
        log "✅ Health monitoring test passed"
    else
        log "⚠️ Health monitoring test showed issues (expected if system is unhealthy)"
    fi
    
    # Test cross-agent monitoring (non-destructive)
    if "$SCRIPT_DIR/cross-agent-reset.sh" --monitor marvin 18789; then
        log "✅ Cross-agent monitoring test passed"
    else
        log "⚠️ Cross-agent monitoring test failed (expected if Marvin is offline)"
    fi
    
    # Check cron jobs are installed
    if crontab -l 2>/dev/null | grep -q "health-monitor.sh"; then
        log "✅ Health monitoring cron job installed"
    else
        log "❌ Health monitoring cron job missing"
        return 1
    fi
    
    log "✅ Monitoring system test completed"
}

# Main installation
main() {
    local action="${1:-install}"
    
    case "$action" in
        "install")
            log "=== Installing OpenClaw Agent Failsafe System ==="
            make_scripts_executable
            setup_health_monitoring_cron
            setup_cross_agent_monitoring_cron
            create_emergency_service
            setup_log_rotation
            create_emergency_alias
            test_monitoring_system
            log "=== Failsafe system installation complete! ==="
            log ""
            log "🟢 System is now protected with:"
            log "   • Health monitoring every 5 minutes"
            log "   • Cross-agent monitoring"
            log "   • Emergency systemd service"
            log "   • Automatic log rotation"
            log "   • Emergency reset aliases"
            log ""
            log "📖 View status: systemctl --user status openclaw-emergency-monitor.timer"
            log "📋 View logs: tail -f ~/.openclaw/logs/agent-*.log"
            log "🆘 Emergency reset: source ~/.openclaw/aliases.sh && magi-reset"
            ;;
        "uninstall")
            log "=== Uninstalling OpenClaw Agent Failsafe System ==="
            # Remove cron jobs
            crontab -l 2>/dev/null | grep -v -E "(health-monitor|cross-agent-reset|logrotate.*openclaw)" | crontab - 2>/dev/null || true
            # Stop and disable systemd service
            systemctl --user stop openclaw-emergency-monitor.timer 2>/dev/null || true
            systemctl --user disable openclaw-emergency-monitor.timer 2>/dev/null || true
            rm -f "$HOME/.config/systemd/user/openclaw-emergency-monitor."*
            systemctl --user daemon-reload
            # Remove aliases
            rm -f "$HOME/.openclaw/aliases.sh"
            log "=== Failsafe system uninstalled ==="
            ;;
        "test")
            test_monitoring_system
            ;;
        *)
            echo "Usage: $0 {install|uninstall|test}"
            echo "  install   - Install complete failsafe monitoring system"
            echo "  uninstall - Remove all failsafe components"
            echo "  test      - Test monitoring system functionality"
            exit 1
            ;;
    esac
}

main "$@"