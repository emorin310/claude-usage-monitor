#!/bin/bash
# Discord Command Handler for Agent Failsafe
# Handles emergency commands via Discord mentions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/.openclaw/logs/discord-commands.log"

# Ensure log file exists
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] DISCORD_CMD: $*" | tee -a "$LOG_FILE"
}

# Send Discord response
send_response() {
    local message="$1"
    local urgent="${2:-false}"
    
    if [[ "$urgent" == "true" ]]; then
        message="🚨 **EMERGENCY** 🚨\n$message"
    fi
    
    # Try to send via OpenClaw message tool
    if command -v openclaw >/dev/null 2>&1; then
        timeout 30 openclaw message send --channel discord \
                --target emorin310 \
                --message "$message" 2>/dev/null || {
            log "❌ Failed to send Discord response"
        }
    fi
}

# Handle failsafe commands
handle_failsafe_command() {
    local command="$1"
    local args="$2"
    
    log "Processing failsafe command: $command $args"
    
    case "$command" in
        "reset")
            case "$args" in
                "magi"|"myself"|"me"|"")
                    log "Emergency reset requested for Magi"
                    send_response "🤖 **Magi Emergency Reset Initiated**\nPerforming full system reset..." true
                    
                    # Execute the reset in background
                    nohup "$SCRIPT_DIR/failsafe-controller.sh" --emergency-reset magi > "/tmp/magi-reset.log" 2>&1 &
                    local reset_pid=$!
                    
                    # Wait a moment and check if reset started
                    sleep 3
                    if kill -0 $reset_pid 2>/dev/null; then
                        send_response "✅ Reset procedure started (PID: $reset_pid)\nMonitoring progress..."
                        # The reset process will send its own completion notification
                    else
                        send_response "❌ Failed to start reset procedure. Check logs." true
                    fi
                    ;;
                "marvin")
                    log "Cross-agent reset requested for Marvin"
                    send_response "🔄 **Requesting Marvin Reset**\nSending reset commands via MQTT and API..."
                    
                    "$SCRIPT_DIR/cross-agent-reset.sh" --reset-other marvin "discord_command_reset" 18789
                    
                    send_response "📡 Reset commands sent to Marvin via multiple channels"
                    ;;
                *)
                    send_response "❓ Unknown reset target: $args\nValid: 'magi', 'marvin', or leave empty for self"
                    ;;
            esac
            ;;
        "status"|"health")
            log "Health status requested"
            send_response "🔍 **Checking Agent Health...**"
            
            # Run health check
            local health_output
            health_output=$("$SCRIPT_DIR/health-monitor.sh" check-all 2>&1) || true
            
            # Format health output for Discord
            local formatted_health="📊 **Agent Health Status**\n\`\`\`\n$health_output\n\`\`\`"
            send_response "$formatted_health"
            ;;
        "backup")
            log "Configuration backup requested"
            send_response "💾 **Creating Configuration Backup...**"
            
            # Create backup
            local backup_dir="$HOME/.openclaw/backups/manual-$(date +%Y%m%d-%H%M%S)"
            mkdir -p "$backup_dir"
            
            if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
                cp "$HOME/.openclaw/openclaw.json" "$backup_dir/"
                cp -r "$HOME/clawd/memory" "$backup_dir/" 2>/dev/null || true
                
                send_response "✅ **Backup Created**\nLocation: \`$backup_dir\`\nContains: config + memory files"
            else
                send_response "❌ No configuration file found to backup"
            fi
            ;;
        "logs")
            log "Log access requested"
            
            # Get recent failsafe logs
            local recent_logs
            recent_logs=$(tail -n 20 "$HOME/.openclaw/logs/agent-"*.log 2>/dev/null | tail -n 10) || recent_logs="No recent logs found"
            
            local formatted_logs="📋 **Recent Failsafe Logs**\n\`\`\`\n$recent_logs\n\`\`\`"
            send_response "$formatted_logs"
            ;;
        "help")
            local help_message="🤖 **Magi Failsafe Commands**

**Emergency Commands:**
• \`@magi reset\` - Emergency reset myself
• \`@magi reset marvin\` - Request Marvin reset  

**Status Commands:**
• \`@magi status\` - Check health of all agents
• \`@magi logs\` - Show recent failsafe logs
• \`@magi backup\` - Create manual config backup

**Info:**
• System monitors health every 5 minutes
• Auto-reset triggers after 3 consecutive failures
• All actions are logged and backed up"

            send_response "$help_message"
            ;;
        *)
            send_response "❓ Unknown failsafe command: $command\nTry: \`@magi help\` for available commands"
            ;;
    esac
}

# Parse Discord mention and extract command
parse_discord_mention() {
    local message="$1"
    
    log "Parsing Discord message: $message"
    
    # Remove @magi mention and clean up
    local cleaned_message
    cleaned_message=$(echo "$message" | sed -E 's/@magi\s*//i' | sed 's/^\s*//;s/\s*$//' | tr '[:upper:]' '[:lower:]')
    
    # Extract command and arguments
    local command
    local args
    
    if [[ "$cleaned_message" =~ ^([a-zA-Z]+)(\s+(.*))?$ ]]; then
        command="${BASH_REMATCH[1]}"
        args="${BASH_REMATCH[3]:-}"
    else
        command="help"
        args=""
    fi
    
    log "Parsed command: '$command' args: '$args'"
    
    # Handle the command
    handle_failsafe_command "$command" "$args"
}

# Main execution
main() {
    local action="$1"
    local message="${2:-}"
    
    case "$action" in
        "--parse-mention")
            parse_discord_mention "$message"
            ;;
        "--test")
            log "Testing Discord command handler"
            parse_discord_mention "@magi status"
            ;;
        *)
            echo "Usage: $0 {--parse-mention|--test} [message]"
            echo "  --parse-mention: Parse a Discord mention and execute command"
            echo "  --test: Test the command handler"
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