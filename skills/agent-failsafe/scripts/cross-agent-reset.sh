#!/bin/bash
# Cross-Agent Reset - Allows agents to reset each other
# Part of Agent Failsafe System

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/.openclaw/logs/cross-agent.log"

# Ensure log file exists
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] CROSS-AGENT: $*" | tee -a "$LOG_FILE"
}

# MQTT-based reset (for Marvin communication)
send_reset_via_mqtt() {
    local target_agent="$1"
    local reason="$2"
    
    log "Sending MQTT reset command to $target_agent: $reason"
    
    # Try to send MQTT message if mosquitto tools available
    if command -v mosquitto_pub >/dev/null 2>&1; then
        local mqtt_message="{
            \"command\": \"failsafe_reset\",
            \"reason\": \"$reason\",
            \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)\",
            \"sender\": \"magi\"
        }"
        
        mosquitto_pub -h localhost -t "homelab/agents/$target_agent/reset" \
                     -m "$mqtt_message" -q 1 2>/dev/null && {
            log "✅ MQTT reset command sent to $target_agent"
            return 0
        } || {
            log "❌ Failed to send MQTT reset command to $target_agent"
            return 1
        }
    else
        log "❌ MQTT tools not available"
        return 1
    fi
}

# HTTP API-based reset (direct gateway communication)
send_reset_via_api() {
    local target_agent="$1"
    local reason="$2"
    local target_port="${3:-18789}"  # Default to Marvin's port
    
    log "Sending API reset command to $target_agent on port $target_port: $reason"
    
    local reset_payload="{
        \"action\": \"failsafe_reset\",
        \"reason\": \"$reason\",
        \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)\",
        \"sender\": \"magi\"
    }"
    
    # Try to send API reset command
    if curl -s -m 30 -X POST "http://localhost:$target_port/api/agents/reset" \
            -H "Content-Type: application/json" \
            -d "$reset_payload" >/dev/null 2>&1; then
        log "✅ API reset command sent to $target_agent"
        return 0
    else
        log "❌ Failed to send API reset command to $target_agent"
        return 1
    fi
}

# Discord-based reset (emergency notification)
send_reset_via_discord() {
    local target_agent="$1"
    local reason="$2"
    
    log "Sending Discord reset notification for $target_agent: $reason"
    
    local discord_message="🚨 **CROSS-AGENT RESET REQUEST**
Agent: $target_agent
Reason: $reason
Time: $(date)

@$target_agent please reset yourself immediately.

Manual reset command: \`$SCRIPT_DIR/failsafe-controller.sh --emergency-reset $target_agent\`"
    
    if command -v openclaw >/dev/null 2>&1; then
        timeout 30 openclaw message send --channel discord \
                --target emorin310 \
                --message "$discord_message" 2>/dev/null && {
            log "✅ Discord reset notification sent"
            return 0
        } || {
            log "❌ Failed to send Discord reset notification"
            return 1
        }
    else
        log "❌ OpenClaw command not available for Discord notification"
        return 1
    fi
}

# Monitor other agent health and trigger reset if needed
monitor_other_agent() {
    local target_agent="$1"
    local target_port="${2:-18789}"
    
    log "Monitoring health of $target_agent"
    
    # Check if target agent is responding
    local health_check_url="http://localhost:$target_port/health"
    
    if ! curl -s -m 10 "$health_check_url" >/dev/null 2>&1; then
        log "❌ $target_agent is not responding on port $target_port"
        
        # Try multiple reset methods
        log "Attempting to reset $target_agent via multiple methods"
        
        # Method 1: MQTT
        send_reset_via_mqtt "$target_agent" "health_check_failed" || true
        
        # Method 2: API (might fail but worth trying)
        send_reset_via_api "$target_agent" "health_check_failed" "$target_port" || true
        
        # Method 3: Discord notification
        send_reset_via_discord "$target_agent" "health_check_failed" || true
        
        log "Reset attempts completed for $target_agent"
        return 1
    else
        log "✅ $target_agent is responding normally"
        return 0
    fi
}

# Handle incoming reset requests (for when other agents reset us)
handle_reset_request() {
    local sender="$1"
    local reason="$2"
    
    log "🚨 RESET REQUEST received from $sender: $reason"
    
    # Verify the request is legitimate (basic safety check)
    case "$sender" in
        "marvin"|"magi"|"eric"|"system")
            log "✅ Reset request from authorized sender: $sender"
            ;;
        *)
            log "❌ Reset request from unknown sender: $sender - IGNORED"
            return 1
            ;;
    esac
    
    # Log the reset request
    echo "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ) CROSS_AGENT_RESET sender=$sender reason=$reason" >> "$HOME/.openclaw/logs/reset-requests.log"
    
    # Execute the reset
    log "Executing self-reset due to request from $sender"
    "$SCRIPT_DIR/failsafe-controller.sh" --emergency-reset magi
}

# Set up cross-agent monitoring cron job
setup_monitoring_cron() {
    log "Setting up cross-agent monitoring cron job"
    
    # Create cron entry for monitoring Marvin every 5 minutes
    local cron_entry="*/5 * * * * $SCRIPT_DIR/cross-agent-reset.sh --monitor marvin 18789 >/dev/null 2>&1"
    
    # Add to crontab if not already present
    (crontab -l 2>/dev/null || true; echo "$cron_entry") | crontab - 2>/dev/null || {
        log "❌ Failed to setup monitoring cron job"
        return 1
    }
    
    log "✅ Cross-agent monitoring cron job setup complete"
}

# Main execution
main() {
    local action="$1"
    local target="${2:-marvin}"
    local reason="${3:-manual_trigger}"
    
    case "$action" in
        "--monitor")
            monitor_other_agent "$target" "${3:-18789}"
            ;;
        "--reset-other")
            log "Manual reset request for $target: $reason"
            send_reset_via_mqtt "$target" "$reason" || true
            send_reset_via_api "$target" "$reason" "${4:-18789}" || true
            send_reset_via_discord "$target" "$reason" || true
            ;;
        "--handle-request")
            handle_reset_request "$target" "$reason"
            ;;
        "--setup-monitoring")
            setup_monitoring_cron
            ;;
        *)
            echo "Usage: $0 {--monitor|--reset-other|--handle-request|--setup-monitoring} [target] [reason] [port]"
            echo "  --monitor: Check health of another agent"
            echo "  --reset-other: Request reset of another agent"
            echo "  --handle-request: Handle incoming reset request"
            echo "  --setup-monitoring: Setup cross-agent monitoring cron"
            exit 1
            ;;
    esac
}

# Command line interface
if [[ $# -eq 0 ]]; then
    echo "Error: No action specified"
    main "--help"
    exit 1
fi

main "$@"