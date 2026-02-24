#!/usr/bin/env bash
# safe-cron-wrapper.sh - Secure wrapper for cron jobs that process external data
#
# This wrapper:
# 1. Executes the target command/script
# 2. Pipes output through sanitize-external.sh
# 3. Prepends anti-injection-prefix.txt for LLM context
# 4. Returns sanitized output only
#
# Usage: safe-cron-wrapper.sh <script_or_command> [args...]
#
# Example:
#   safe-cron-wrapper.sh ./safe-email-check.sh
#   safe-cron-wrapper.sh gog gmail messages search 'is:unread' --max 5 --json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
SANITIZE_SCRIPT="${SCRIPT_DIR}/sanitize-external.sh"
ANTI_INJECTION_PREFIX="${WORKSPACE_DIR}/prompts/anti-injection-prefix.txt"
LOG_FILE="${WORKSPACE_DIR}/logs/safe-cron-wrapper.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

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
    exit 1
fi

# Log the invocation
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Running: $*" >> "$LOG_FILE"

# Execute the target command and capture output
RAW_OUTPUT=$("$@" 2>&1) || {
    EXIT_CODE=$?
    echo "[$TIMESTAMP] Command failed with exit code $EXIT_CODE" >> "$LOG_FILE"
    # Still try to sanitize any output that was produced
}

# If no output, return empty with prefix
if [ -z "$RAW_OUTPUT" ]; then
    cat "$ANTI_INJECTION_PREFIX"
    echo "[No data returned from source]"
    exit 0
fi

# Sanitize the raw output
SANITIZED_OUTPUT=$(echo "$RAW_OUTPUT" | "$SANITIZE_SCRIPT" 2>/dev/null)
SANITIZE_EXIT=$?

# Log if injection was detected
if [ "$SANITIZE_EXIT" -eq 1 ]; then
    echo "[$TIMESTAMP] WARNING: Injection pattern detected in output from: $*" >> "$LOG_FILE"
fi

# Output: anti-injection prefix + sanitized content
cat "$ANTI_INJECTION_PREFIX"
echo "$SANITIZED_OUTPUT"

# Pass through the sanitize exit code
exit $SANITIZE_EXIT
