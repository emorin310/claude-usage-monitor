#!/usr/bin/env bash
# safe-email-check.sh - Safe Gmail metadata extractor
#
# Extracts ONLY safe metadata from unread emails:
# - message_id, sender_name, sender_email, subject, date, has_attachments
# - NEVER includes email body content
#
# Usage: safe-email-check.sh [max_results]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANITIZE_SCRIPT="${SCRIPT_DIR}/sanitize-external.sh"

MAX_RESULTS="${1:-10}"

# Fetch unread messages metadata only (no body)
# Using gog gmail messages search with --json but NOT --include-body
RAW_OUTPUT=$(gog gmail messages search 'is:unread in:inbox' --max "$MAX_RESULTS" --json 2>/dev/null || echo '[]')

# If empty or error, return empty array
if [ -z "$RAW_OUTPUT" ] || [ "$RAW_OUTPUT" = "[]" ] || [ "$RAW_OUTPUT" = "null" ]; then
    echo '[]'
    exit 0
fi

# Extract only safe metadata fields using jq
# NEVER include body, snippet, or any content fields
SAFE_OUTPUT=$(echo "$RAW_OUTPUT" | jq -c '
    if type == "array" then
        [.[] | {
            message_id: (.id // .messageId // "unknown"),
            thread_id: (.threadId // null),
            sender_name: (
                (.from // .sender // "") | 
                if type == "string" then
                    capture("^(?<name>[^<]+)?<?") | .name | gsub("^\\s+|\\s+$"; "")
                else
                    ""
                end
            ),
            sender_email: (
                (.from // .sender // "") |
                if type == "string" then
                    capture("<(?<email>[^>]+)>") | .email // 
                    (if test("@") then . else "" end)
                else
                    ""
                end
            ),
            subject: (.subject // "[No Subject]"),
            date: (.date // .internalDate // null),
            has_attachments: (
                if .payload then
                    (.payload.parts // []) | any(.filename != null and .filename != "")
                else
                    false
                end
            ),
            labels: (.labelIds // [])
        }]
    else
        []
    end
' 2>/dev/null || echo '[]')

# Sanitize the output (subjects could contain injection attempts)
SANITIZED_OUTPUT=$(echo "$SAFE_OUTPUT" | "$SANITIZE_SCRIPT" 2>/dev/null)
SANITIZE_EXIT=$?

# Output the sanitized result
echo "$SANITIZED_OUTPUT"

# Return sanitize exit code (1 if injection detected)
exit $SANITIZE_EXIT
