#!/bin/bash
# Agent Health Monitor - Detects when agents are in broken states
# Part of Agent Failsafe System

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../configs"
LOG_FILE="$HOME/.openclaw/logs/agent-health.log"

# Ensure log file exists
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Check if OpenClaw gateway is responding
check_gateway() {
    local agent_name="$1"
    log "Checking gateway health for $agent_name..."
    
    # Try to get status via openclaw command
    if timeout 30 openclaw status >/dev/null 2>&1; then
        log "✅ Gateway responding for $agent_name"
        return 0
    else
        log "❌ Gateway not responding for $agent_name"
        return 1
    fi
}

# Check heartbeat responsiveness
check_heartbeat() {
    local agent_name="$1"
    log "Checking heartbeat for $agent_name..."
    
    # Check if heartbeat file is recent (within last 35 minutes)
    local heartbeat_file="$HOME/.openclaw/logs/heartbeat-state.json"
    
    if [[ -f "$heartbeat_file" ]]; then
        local last_heartbeat=$(stat -c %Y "$heartbeat_file" 2>/dev/null || echo 0)
        local current_time=$(date +%s)
        local age=$((current_time - last_heartbeat))
        
        if [[ $age -lt 2100 ]]; then  # 35 minutes
            log "✅ Heartbeat recent for $agent_name (${age}s ago)"
            return 0
        else
            log "❌ Heartbeat stale for $agent_name (${age}s ago)"
            return 1
        fi
    else
        log "❌ No heartbeat file found for $agent_name"
        return 1
    fi
}

# Check model authentication
check_model_auth() {
    local agent_name="$1"
    log "Checking model authentication for $agent_name..."
    
    # Try a simple model test
    if timeout 60 openclaw test --model anthropic/claude-sonnet-4-20250514 --message "test" >/dev/null 2>&1; then
        log "✅ Model authentication working for $agent_name"
        return 0
    else
        log "❌ Model authentication failed for $agent_name"
        return 1
    fi
}

# Check configuration integrity
check_config() {
    local agent_name="$1"
    log "Checking configuration integrity for $agent_name..."
    
    local config_file="$HOME/.openclaw/openclaw.json"
    
    if [[ -f "$config_file" ]]; then
        if jq empty "$config_file" >/dev/null 2>&1; then
            log "✅ Configuration file valid for $agent_name"
            return 0
        else
            log "❌ Configuration file corrupted for $agent_name"
            return 1
        fi
    else
        log "❌ Configuration file missing for $agent_name"
        return 1
    fi
}

# Check Discord connectivity
check_discord() {
    local agent_name="$1"
    log "Checking Discord connectivity for $agent_name..."
    
    # Parse status output for Discord channel state
    if openclaw status 2>/dev/null | grep -q "Discord.*ON.*OK"; then
        log "✅ Discord connectivity good for $agent_name"
        return 0
    else
        log "❌ Discord connectivity issues for $agent_name"
        return 1
    fi
}

# Overall health assessment
assess_agent_health() {
    local agent_name="$1"
    local failures=0
    
    log "=== Health Assessment for $agent_name ==="
    
    check_gateway "$agent_name" || ((failures++))
    check_heartbeat "$agent_name" || ((failures++))
    check_model_auth "$agent_name" || ((failures++))
    check_config "$agent_name" || ((failures++))
    check_discord "$agent_name" || ((failures++))
    
    log "=== Health Assessment Complete: $failures failures ==="
    
    if [[ $failures -eq 0 ]]; then
        log "🟢 Agent $agent_name is HEALTHY"
        return 0
    elif [[ $failures -le 2 ]]; then
        log "🟡 Agent $agent_name is DEGRADED ($failures issues)"
        return 1
    else
        log "🔴 Agent $agent_name is CRITICAL ($failures failures)"
        return 2
    fi
}

# Check if failsafe should trigger
should_trigger_failsafe() {
    local health_code="$1"
    local agent_name="$2"
    
    # Track consecutive failures
    local failure_count_file="/tmp/agent-${agent_name}-failures"
    
    if [[ $health_code -eq 0 ]]; then
        # Reset failure count on success
        rm -f "$failure_count_file"
        return 1
    fi
    
    # Increment failure count
    local current_failures=0
    if [[ -f "$failure_count_file" ]]; then
        current_failures=$(cat "$failure_count_file")
    fi
    
    current_failures=$((current_failures + 1))
    echo "$current_failures" > "$failure_count_file"
    
    log "Agent $agent_name failure count: $current_failures"
    
    # Trigger failsafe after 3 consecutive failures or 1 critical failure
    if [[ $current_failures -ge 3 ]] || [[ $health_code -eq 2 ]]; then
        log "🚨 FAILSAFE TRIGGER for $agent_name"
        return 0
    fi
    
    return 1
}

# Main execution
main() {
    local agent_name="${1:-magi}"
    local check_only="${2:-false}"
    
    log "Starting health monitor for agent: $agent_name"
    
    assess_agent_health "$agent_name"
    health_result=$?
    
    if [[ "$check_only" == "true" ]]; then
        exit $health_result
    fi
    
    if should_trigger_failsafe $health_result "$agent_name"; then
        log "🚨 TRIGGERING FAILSAFE for $agent_name"
        "$SCRIPT_DIR/failsafe-controller.sh" --auto-reset "$agent_name"
    fi
}

# Command line interface
case "${1:-check}" in
    "check-all")
        main "magi" true
        magi_result=$?
        echo "Magi health: $magi_result"
        ;;
    "monitor")
        main "${2:-magi}" false
        ;;
    "check")
        main "${2:-magi}" true
        ;;
    *)
        echo "Usage: $0 {check-all|monitor|check} [agent_name]"
        echo "  check-all: Check health of all agents"
        echo "  monitor: Continuous monitoring with failsafe triggers"
        echo "  check: One-time health check only"
        exit 1
        ;;
esac