#!/bin/bash
# Test Agent Failsafe System
# Verifies all components are working correctly

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/../configs"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    local status="$1"
    local message="$2"
    
    case "$status" in
        "PASS")
            echo -e "${GREEN}✅ PASS${NC} $message"
            ;;
        "FAIL")
            echo -e "${RED}❌ FAIL${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠️  WARN${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  INFO${NC} $message"
            ;;
    esac
}

# Test script executability
test_scripts_executable() {
    print_status "INFO" "Testing script executability..."
    
    local scripts=(
        "health-monitor.sh"
        "failsafe-controller.sh"
        "cross-agent-reset.sh"
        "discord-commands.sh"
        "setup-monitoring.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -x "$SCRIPT_DIR/$script" ]]; then
            print_status "PASS" "Script executable: $script"
        else
            print_status "FAIL" "Script not executable: $script"
            return 1
        fi
    done
}

# Test configuration files exist
test_config_files() {
    print_status "INFO" "Testing configuration files..."
    
    if [[ -f "$CONFIG_DIR/base-safe.json" ]]; then
        if jq empty "$CONFIG_DIR/base-safe.json" >/dev/null 2>&1; then
            print_status "PASS" "Safe configuration file valid"
        else
            print_status "FAIL" "Safe configuration file invalid JSON"
            return 1
        fi
    else
        print_status "FAIL" "Safe configuration file missing"
        return 1
    fi
}

# Test health monitoring (non-destructive)
test_health_monitoring() {
    print_status "INFO" "Testing health monitoring..."
    
    # Run health check
    if "$SCRIPT_DIR/health-monitor.sh" check magi >/dev/null 2>&1; then
        local exit_code=$?
        case $exit_code in
            0)
                print_status "PASS" "Health check passed - system healthy"
                ;;
            1)
                print_status "WARN" "Health check shows degraded state (expected if issues exist)"
                ;;
            2)
                print_status "WARN" "Health check shows critical state (expected if major issues exist)"
                ;;
            *)
                print_status "FAIL" "Health check failed with unexpected code: $exit_code"
                return 1
                ;;
        esac
    else
        print_status "FAIL" "Health check script failed to run"
        return 1
    fi
}

# Test Discord command parsing
test_discord_commands() {
    print_status "INFO" "Testing Discord command parsing..."
    
    # Test command parsing (non-destructive)
    if "$SCRIPT_DIR/discord-commands.sh" --test >/dev/null 2>&1; then
        print_status "PASS" "Discord command parsing works"
    else
        print_status "FAIL" "Discord command parsing failed"
        return 1
    fi
}

# Test cross-agent monitoring (non-destructive)
test_cross_agent() {
    print_status "INFO" "Testing cross-agent monitoring..."
    
    # Test Marvin connectivity (non-destructive check)
    if "$SCRIPT_DIR/cross-agent-reset.sh" --monitor marvin 18789 >/dev/null 2>&1; then
        print_status "PASS" "Marvin connectivity check passed"
    else
        print_status "WARN" "Marvin connectivity check failed (expected if Marvin offline)"
    fi
}

# Test backup functionality
test_backup_functionality() {
    print_status "INFO" "Testing backup functionality..."
    
    # Test backup creation (safe operation)
    local test_backup_dir="/tmp/failsafe-test-backup-$$"
    mkdir -p "$test_backup_dir"
    
    # Simulate backup
    if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
        cp "$HOME/.openclaw/openclaw.json" "$test_backup_dir/" 2>/dev/null && {
            print_status "PASS" "Configuration backup test successful"
            rm -rf "$test_backup_dir"
        } || {
            print_status "FAIL" "Configuration backup test failed"
            return 1
        }
    else
        print_status "WARN" "No active configuration to test backup with"
    fi
}

# Test log file creation
test_log_files() {
    print_status "INFO" "Testing log file handling..."
    
    local log_dir="$HOME/.openclaw/logs"
    
    if [[ -d "$log_dir" ]] || mkdir -p "$log_dir" 2>/dev/null; then
        print_status "PASS" "Log directory accessible"
        
        # Test log file creation
        local test_log="$log_dir/failsafe-test.log"
        if echo "test" > "$test_log" 2>/dev/null; then
            print_status "PASS" "Log file creation works"
            rm -f "$test_log"
        else
            print_status "FAIL" "Cannot create log files"
            return 1
        fi
    else
        print_status "FAIL" "Cannot access or create log directory"
        return 1
    fi
}

# Test OpenClaw integration
test_openclaw_integration() {
    print_status "INFO" "Testing OpenClaw integration..."
    
    if command -v openclaw >/dev/null 2>&1; then
        print_status "PASS" "OpenClaw command available"
        
        # Test status command (safe)
        if timeout 10 openclaw status >/dev/null 2>&1; then
            print_status "PASS" "OpenClaw status command works"
        else
            print_status "WARN" "OpenClaw status command timeout/failed"
        fi
    else
        print_status "FAIL" "OpenClaw command not available"
        return 1
    fi
}

# Test cron job format
test_cron_format() {
    print_status "INFO" "Testing cron job format..."
    
    # Check if crontab is accessible
    if crontab -l >/dev/null 2>&1; then
        print_status "PASS" "Crontab accessible"
        
        # Check for existing failsafe cron jobs
        if crontab -l 2>/dev/null | grep -q "health-monitor"; then
            print_status "PASS" "Health monitoring cron job found"
        else
            print_status "WARN" "No health monitoring cron job installed"
        fi
    else
        print_status "WARN" "Crontab not accessible (might be in restricted environment)"
    fi
}

# Run comprehensive test
run_comprehensive_test() {
    print_status "INFO" "Starting Agent Failsafe System Test..."
    echo
    
    local tests=(
        test_scripts_executable
        test_config_files
        test_log_files
        test_openclaw_integration
        test_health_monitoring
        test_discord_commands
        test_cross_agent
        test_backup_functionality
        test_cron_format
    )
    
    local passed=0
    local total=${#tests[@]}
    
    for test_func in "${tests[@]}"; do
        if $test_func; then
            ((passed++))
        fi
        echo
    done
    
    echo "========================================="
    print_status "INFO" "Test Summary: $passed/$total tests passed"
    
    if [[ $passed -eq $total ]]; then
        print_status "PASS" "All tests passed! Failsafe system ready."
        return 0
    elif [[ $passed -gt $((total / 2)) ]]; then
        print_status "WARN" "Most tests passed. Some warnings - system should work."
        return 1
    else
        print_status "FAIL" "Multiple test failures. System needs attention."
        return 2
    fi
}

# Quick smoke test
run_smoke_test() {
    print_status "INFO" "Running quick smoke test..."
    
    test_scripts_executable && \
    test_config_files && \
    test_openclaw_integration && {
        print_status "PASS" "Smoke test passed - basic functionality verified"
        return 0
    } || {
        print_status "FAIL" "Smoke test failed - check system configuration"  
        return 1
    }
}

# Main execution
main() {
    local test_type="${1:-comprehensive}"
    
    case "$test_type" in
        "smoke")
            run_smoke_test
            ;;
        "comprehensive"|"full")
            run_comprehensive_test
            ;;
        *)
            echo "Usage: $0 {smoke|comprehensive}"
            echo "  smoke        - Quick basic functionality test"
            echo "  comprehensive - Full system test (default)"
            exit 1
            ;;
    esac
}

main "$@"