#!/usr/bin/env bash
# cron-wrapper.sh - Secure wrapper for cron jobs processing external data
#
# This wrapper:
# 1. Executes the target command/script
# 2. Pipes output through sanitize.sh
# 3. Prepends anti-injection prompt prefix
# 4. Returns sanitized output ready for LLM consumption
#
# Usage: 
#   cron-wrapper.sh <script_or_command> [args...]
#   cron-wrapper.sh ./my-email-checker.sh
#   cron-wrapper.sh curl -s "https://api.example.com/feed"
#
# Environment Variables:
#   INJECTION_LOG_DIR      - Directory for logs (default: ~/logs)
#   INJECTION_PREFIX_FILE  - Custom prefix file path
#   CRON_WRAPPER_QUIET     - Set to "1" to suppress the prefix

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SANITIZE_SCRIPT="${SCRIPT_DIR}/sanitize.sh"
ANTI_INJECTION_PREFIX="${INJECTION_PREFIX_FILE:-${SKILL_DIR}/prompts/anti-injection-prefix.txt}"

# Log configuration
LOG_DIR="${INJECTION_LOG_DIR:-${HOME}/logs}"
LOG_FILE="${LOG_DIR}/cron-wrapper.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR" 2>/dev/null || true

# Log function
log_msg() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" >> "$LOG_FILE" 2>/dev/null || true
}

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <script_or_command> [args...]" >&2
    exit 1
fi

# Check required files exist
if [ ! -f "$SANITIZE_SCRIPT" ]; then
    echo "Error: Sanitize script not found: $SANITIZE_SCRIPT" >&2
    exit 1
fi

if [ ! -f "$ANTI_INJECTION_PREFIX" ]; then
    echo "Error: Anti-injection prefix not found: $ANTI_INJECTION_PREFIX" >&2
    echo "Create one or set INJECTION_PREFIX_FILE to an existing file" >&2
    exit 1
fi

log_msg "Running: $*"

# Execute the target command and capture output
RAW_OUTPUT=""
COMMAND_EXIT=0
RAW_OUTPUT=$("$@" 2>&1) || COMMAND_EXIT=$?

if [ "$COMMAND_EXIT" -ne 0 ]; then
    log_msg "Command failed with exit code $COMMAND_EXIT"
fi

# If no output, return with prefix + empty notice
if [ -z "$RAW_OUTPUT" ]; then
    if [ "${CRON_WRAPPER_QUIET:-}" != "1" ]; then
        cat "$ANTI_INJECTION_PREFIX"
    fi
    echo "[No data returned from source]"
    exit 0
fi

# Sanitize the raw output
SANITIZED_OUTPUT=$(echo "$RAW_OUTPUT" | "$SANITIZE_SCRIPT" 2>/dev/null)
SANITIZE_EXIT=$?

# Log if injection was detected
if [ "$SANITIZE_EXIT" -eq 1 ]; then
    log_msg "WARNING: Injection pattern detected in output from: $*"
fi

# Output: anti-injection prefix + sanitized content
if [ "${CRON_WRAPPER_QUIET:-}" != "1" ]; then
    cat "$ANTI_INJECTION_PREFIX"
fi
echo "$SANITIZED_OUTPUT"

# Pass through the sanitize exit code
exit $SANITIZE_EXIT
