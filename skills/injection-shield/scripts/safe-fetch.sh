#!/usr/bin/env bash
# safe-fetch.sh - Generic safe external data fetcher
#
# Wraps any command that fetches external data and sanitizes the output.
# Designed for use with email checkers, API calls, web scrapers, etc.
#
# Usage: 
#   safe-fetch.sh <command> [args...]
#   safe-fetch.sh curl -s "https://api.example.com/data"
#   safe-fetch.sh gog gmail messages search 'is:unread' --json
#
# Environment Variables:
#   INJECTION_LOG_DIR      - Directory for logs (default: ~/logs)
#   SAFE_FETCH_TIMEOUT     - Command timeout in seconds (default: 30)
#   SAFE_FETCH_MAX_SIZE    - Max output size in bytes (default: 1MB)
#
# Exit codes:
#   0 - Clean (no injection detected)
#   1 - Injection detected (output still provided, sanitized)
#   2 - Command failed
#   3 - Timeout

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANITIZE_SCRIPT="${SCRIPT_DIR}/sanitize.sh"

# Configuration
TIMEOUT="${SAFE_FETCH_TIMEOUT:-30}"
MAX_SIZE="${SAFE_FETCH_MAX_SIZE:-1048576}"  # 1MB default
LOG_DIR="${INJECTION_LOG_DIR:-${HOME}/logs}"
LOG_FILE="${LOG_DIR}/safe-fetch.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR" 2>/dev/null || true

# Check arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <command> [args...]" >&2
    echo "Example: $0 curl -s https://api.example.com/data" >&2
    exit 2
fi

# Check sanitize script exists
if [ ! -f "$SANITIZE_SCRIPT" ]; then
    echo "Error: Sanitize script not found: $SANITIZE_SCRIPT" >&2
    exit 2
fi

# Log function
log_msg() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" >> "$LOG_FILE" 2>/dev/null || true
}

log_msg "Executing: $*"

# Create temp file for output
TEMP_FILE=$(mktemp)
trap "rm -f '$TEMP_FILE'" EXIT

# Execute command with timeout
# Cross-platform timeout handling
COMMAND_EXIT=0
if command -v timeout >/dev/null 2>&1; then
    # GNU coreutils timeout (Linux)
    timeout "$TIMEOUT" "$@" > "$TEMP_FILE" 2>&1 || COMMAND_EXIT=$?
elif command -v gtimeout >/dev/null 2>&1; then
    # GNU coreutils via Homebrew (macOS)
    gtimeout "$TIMEOUT" "$@" > "$TEMP_FILE" 2>&1 || COMMAND_EXIT=$?
else
    # Fallback: no timeout (macOS without coreutils)
    "$@" > "$TEMP_FILE" 2>&1 || COMMAND_EXIT=$?
fi

# Check for timeout (exit code 124 for GNU timeout)
if [ "$COMMAND_EXIT" -eq 124 ]; then
    log_msg "TIMEOUT: Command exceeded ${TIMEOUT}s"
    echo '{"error": "Command timed out", "timeout_seconds": '"$TIMEOUT"'}'
    exit 3
fi

# Check for command failure
if [ "$COMMAND_EXIT" -ne 0 ]; then
    log_msg "FAILED: Exit code $COMMAND_EXIT"
    # Still try to output whatever we got
fi

# Check output size
OUTPUT_SIZE=$(wc -c < "$TEMP_FILE" | tr -d ' ')
if [ "$OUTPUT_SIZE" -gt "$MAX_SIZE" ]; then
    log_msg "WARNING: Output truncated from $OUTPUT_SIZE to $MAX_SIZE bytes"
    head -c "$MAX_SIZE" "$TEMP_FILE" > "${TEMP_FILE}.truncated"
    mv "${TEMP_FILE}.truncated" "$TEMP_FILE"
fi

# If empty output, return empty
if [ "$OUTPUT_SIZE" -eq 0 ]; then
    log_msg "Empty output from command"
    echo '[]'
    exit 0
fi

# Sanitize the output
SANITIZED_OUTPUT=$(cat "$TEMP_FILE" | "$SANITIZE_SCRIPT" 2>/dev/null)
SANITIZE_EXIT=$?

if [ "$SANITIZE_EXIT" -eq 1 ]; then
    log_msg "WARNING: Injection pattern detected in output"
fi

# Output sanitized result
echo "$SANITIZED_OUTPUT"

# Return appropriate exit code
if [ "$COMMAND_EXIT" -ne 0 ]; then
    exit 2
fi
exit $SANITIZE_EXIT
