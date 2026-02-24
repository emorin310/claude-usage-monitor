#!/bin/bash
# Failsafe Controller - Handles agent recovery and rollbacks
# Part of Agent Failsafe System

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../configs"
LOG_FILE="$HOME/.openclaw/logs/agent-failsafe.log"

# Ensure log file exists
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAILSAFE: $*" | tee -a "$LOG_FILE"
}

# Emergency notification
notify_emergency() {
    local message="$1"
    log "🚨 EMERGENCY: $message"
    
    # Try multiple notification methods
    # Discord notification (if working)
    if command -v openclaw >/dev/null 2>&1; then
        timeout 30 openclaw message send --channel discord --target emorin310 --message "🚨 **AGENT FAILSAFE TRIGGERED**\n$message" 2>/dev/null || true
    fi
    
    # System notification
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "OpenClaw Failsafe" "$message" 2>/dev/null || true
    fi
    
    # Log to system journal
    if command -v systemd-cat >/dev/null 2>&1; then
        echo "OpenClaw Failsafe: $message" | systemd-cat -t openclaw-failsafe -p emerg
    fi
}

# Backup current configuration
backup_current_config() {
    local agent_name="$1"
    local backup_dir="$HOME/.openclaw/backups/failsafe-$(date +%Y%m%d-%H%M%S)"
    
    log "Creating configuration backup to $backup_dir"
    mkdir -p "$backup_dir"
    
    # Backup main config
    if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
        cp "$HOME/.openclaw/openclaw.json" "$backup_dir/"
        log "✅ Backed up openclaw.json"
    fi
    
    # Backup sessions (if they exist)
    if [[ -d "$HOME/.openclaw/agents/main/sessions" ]]; then
        cp -r "$HOME/.openclaw/agents/main/sessions" "$backup_dir/"
        log "✅ Backed up session data"
    fi
    
    # Backup memory files
    if [[ -d "$HOME/clawd/memory" ]]; then
        cp -r "$HOME/clawd/memory" "$backup_dir/"
        log "✅ Backed up memory files"
    fi
    
    echo "$backup_dir" > "/tmp/last-failsafe-backup"
    log "Backup complete: $backup_dir"
}

# Restore safe configuration
restore_safe_config() {
    local agent_name="$1"
    
    log "Restoring safe configuration for $agent_name"
    
    # Copy base safe config
    if [[ -f "$CONFIG_DIR/base-safe.json" ]]; then
        cp "$CONFIG_DIR/base-safe.json" "$HOME/.openclaw/openclaw.json"
        log "✅ Restored base safe configuration"
    else
        log "❌ No base safe config found, creating minimal config"
        create_minimal_config
    fi
}

# Create minimal working configuration
create_minimal_config() {
    log "Creating minimal safe configuration"
    
    cat > "$HOME/.openclaw/openclaw.json" << 'EOF'
{
  "meta": {
    "lastTouchedVersion": "2026.2.22",
    "lastTouchedAt": "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514"
      }
    },
    "list": [
      {
        "id": "main",
        "workspace": "/home/magi/clawd",
        "identity": {
          "name": "Magi",
          "emoji": "🏠"
        }
      }
    ]
  },
  "channels": {
    "discord": {
      "enabled": true,
      "dmPolicy": "pairing",
      "groupPolicy": "allowlist",
      "streaming": "partial"
    }
  },
  "gateway": {
    "port": 18790,
    "mode": "local",
    "bind": "lan",
    "controlUi": {
      "allowInsecureAuth": true
    },
    "auth": {
      "mode": "token",
      "rateLimit": {
        "maxAttempts": 10,
        "windowMs": 60000,
        "lockoutMs": 300000
      }
    }
  },
  "plugins": {
    "entries": {
      "discord": {
        "enabled": true
      }
    }
  }
}
EOF
    
    log "✅ Created minimal safe configuration"
}

# Reset model authentication
reset_model_auth() {
    local agent_name="$1"
    
    log "Resetting model authentication for $agent_name"
    
    # Clear any cached auth tokens
    rm -f "$HOME/.openclaw/auth-cache"* 2>/dev/null || true
    
    # Reset to known good model
    jq '.agents.defaults.model.primary = "anthropic/claude-sonnet-4-20250514"' \
        "$HOME/.openclaw/openclaw.json" > "/tmp/openclaw-temp.json" && \
        mv "/tmp/openclaw-temp.json" "$HOME/.openclaw/openclaw.json"
    
    log "✅ Model reset to base sonnet"
}

# Restart OpenClaw services
restart_services() {
    local agent_name="$1"
    
    log "Restarting OpenClaw services for $agent_name"
    
    # Stop gateway
    if systemctl --user is-active --quiet openclaw-gateway 2>/dev/null; then
        log "Stopping OpenClaw gateway..."
        systemctl --user stop openclaw-gateway || true
        sleep 2
    fi
    
    # Start gateway
    log "Starting OpenClaw gateway..."
    systemctl --user start openclaw-gateway || {
        log "❌ Failed to start via systemctl, trying direct command"
        # Fallback: try to start directly
        nohup openclaw gateway start > "$HOME/.openclaw/logs/gateway-failsafe.log" 2>&1 &
        sleep 5
    }
    
    # Wait for gateway to be ready
    local retries=0
    while [[ $retries -lt 30 ]]; do
        if curl -s http://localhost:18790/health >/dev/null 2>&1; then
            log "✅ Gateway is responding"
            return 0
        fi
        ((retries++))
        sleep 2
    done
    
    log "❌ Gateway failed to start properly"
    return 1
}

# Clear problematic session data
clear_sessions() {
    local agent_name="$1"
    
    log "Clearing potentially corrupted session data for $agent_name"
    
    # Clear session files but preserve memory
    local session_dir="$HOME/.openclaw/agents/main/sessions"
    if [[ -d "$session_dir" ]]; then
        # Backup sessions first
        cp -r "$session_dir" "$session_dir.bak.$(date +%s)" 2>/dev/null || true
        
        # Clear session JSON but keep transcript files
        find "$session_dir" -name "sessions.json*" -delete 2>/dev/null || true
        log "✅ Cleared session metadata"
    fi
}

# Full agent reset procedure
perform_full_reset() {
    local agent_name="$1"
    
    notify_emergency "Performing full reset for agent $agent_name"
    
    log "=== STARTING FULL RESET FOR $agent_name ==="
    
    # Step 1: Backup current state
    backup_current_config "$agent_name"
    
    # Step 2: Clear problematic sessions
    clear_sessions "$agent_name"
    
    # Step 3: Restore safe configuration
    restore_safe_config "$agent_name"
    
    # Step 4: Reset model authentication
    reset_model_auth "$agent_name"
    
    # Step 5: Restart services
    if restart_services "$agent_name"; then
        log "✅ Services restarted successfully"
    else
        log "❌ Service restart failed"
        notify_emergency "Failed to restart services for $agent_name - manual intervention required"
        return 1
    fi
    
    # Step 6: Verify recovery
    sleep 10
    if "$SCRIPT_DIR/health-monitor.sh" check "$agent_name"; then
        log "🟢 RECOVERY SUCCESSFUL for $agent_name"
        notify_emergency "✅ Agent $agent_name successfully recovered"
    else
        log "🔴 RECOVERY FAILED for $agent_name"
        notify_emergency "❌ Agent $agent_name recovery failed - manual intervention required"
        return 1
    fi
    
    log "=== FULL RESET COMPLETE FOR $agent_name ==="
}

# Configuration-only rollback
perform_config_rollback() {
    local agent_name="$1"
    
    log "=== STARTING CONFIG ROLLBACK FOR $agent_name ==="
    
    backup_current_config "$agent_name"
    restore_safe_config "$agent_name"
    
    # Restart only the gateway
    systemctl --user restart openclaw-gateway || true
    sleep 5
    
    log "=== CONFIG ROLLBACK COMPLETE FOR $agent_name ==="
}

# Main execution
main() {
    local action="$1"
    local agent_name="${2:-magi}"
    
    case "$action" in
        "--auto-reset")
            log "Auto-reset triggered for $agent_name"
            perform_full_reset "$agent_name"
            ;;
        "--emergency-reset")
            log "Emergency reset triggered for $agent_name"
            perform_full_reset "$agent_name"
            ;;
        "--config-rollback")
            log "Configuration rollback triggered for $agent_name"
            perform_config_rollback "$agent_name"
            ;;
        "--reset-agent")
            log "Manual agent reset triggered for $agent_name"
            perform_full_reset "$agent_name"
            ;;
        *)
            echo "Usage: $0 {--auto-reset|--emergency-reset|--config-rollback|--reset-agent} [agent_name]"
            echo "  --auto-reset: Automated reset triggered by health monitor"
            echo "  --emergency-reset: Manual emergency reset"
            echo "  --config-rollback: Configuration-only rollback"
            echo "  --reset-agent: Full manual reset"
            exit 1
            ;;
    esac
}

# Handle command line arguments
if [[ $# -eq 0 ]]; then
    echo "Error: No action specified"
    main "--help"
    exit 1
fi

main "$@"