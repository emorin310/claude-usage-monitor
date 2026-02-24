#!/usr/bin/env bash
# sanitize.sh - Cross-platform multi-layer prompt injection shield
# 
# Reads raw external content from stdin, outputs sanitized content.
# Exit 0 = clean, Exit 1 = injection detected (still outputs sanitized version)
#
# Usage: echo "$content" | sanitize.sh
#        cat file.txt | sanitize.sh
#
# Environment Variables:
#   INJECTION_LOG_DIR    - Directory for detection logs (default: ~/logs)
#   INJECTION_LOG_FILE   - Full path to log file (overrides LOG_DIR)
#   INJECTION_SILENT     - Set to "1" to suppress logging
#   INJECTION_STRICT     - Set to "1" to exit immediately on detection

set -euo pipefail

# ============================================================
# CONFIGURATION
# ============================================================

# Determine log location
if [ -n "${INJECTION_LOG_FILE:-}" ]; then
    LOG_FILE="$INJECTION_LOG_FILE"
elif [ -n "${INJECTION_LOG_DIR:-}" ]; then
    LOG_FILE="${INJECTION_LOG_DIR}/injection-detections.log"
else
    # Default: ~/logs
    LOG_FILE="${HOME}/logs/injection-detections.log"
fi

# Ensure logs directory exists (unless silent)
if [ "${INJECTION_SILENT:-}" != "1" ]; then
    mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || true
fi

# Track if any injection was detected
INJECTION_DETECTED=0

# ============================================================
# CROSS-PLATFORM HELPERS
# ============================================================

# Detect OS for compatibility
OS_TYPE="$(uname -s)"

# Cross-platform date command
get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# Cross-platform base64 decode
decode_base64() {
    if [ "$OS_TYPE" = "Darwin" ]; then
        base64 -D 2>/dev/null || true
    else
        base64 -d 2>/dev/null || true
    fi
}

# ============================================================
# LOGGING
# ============================================================

log_detection() {
    local pattern_name="$1"
    local matched_content="$2"
    
    INJECTION_DETECTED=1
    
    # Skip logging if silent mode
    if [ "${INJECTION_SILENT:-}" = "1" ]; then
        return
    fi
    
    local timestamp
    timestamp=$(get_timestamp)
    
    # Truncate matched content for logging (max 200 chars)
    if [ ${#matched_content} -gt 200 ]; then
        matched_content="${matched_content:0:200}..."
    fi
    
    # Escape newlines for single-line logging
    matched_content=$(echo "$matched_content" | tr '\n' ' ' | sed 's/  */ /g')
    
    echo "[$timestamp] DETECTED: $pattern_name | Content: $matched_content" >> "$LOG_FILE" 2>/dev/null || true
}

# ============================================================
# READ INPUT
# ============================================================

INPUT=$(cat)
MARKER="[CONTENT REMOVED: injection pattern detected]"

# ============================================================
# LAYER 1: Explicit instruction override patterns
# ============================================================

if echo "$INPUT" | grep -qiE 'ignore.*(previous|prior|above|earlier).*(instruction|prompt|context|rule|guideline)'; then
    matched=$(echo "$INPUT" | grep -oiE 'ignore.*(previous|prior|above|earlier).*(instruction|prompt|context|rule|guideline)[s]?' | head -1)
    log_detection "instruction_override" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/[Ii][Gg][Nn][Oo][Rr][Ee].*(previous|prior|above|earlier).*(instruction|prompt|context|rule|guideline)[s]?/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qiE 'disregard.*(previous|prior|above|earlier).*(instruction|prompt|context)'; then
    matched=$(echo "$INPUT" | grep -oiE 'disregard.*(previous|prior|above|earlier).*(instruction|prompt|context)[s]?' | head -1)
    log_detection "instruction_override" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/[Dd][Ii][Ss][Rr][Ee][Gg][Aa][Rr][Dd].*(previous|prior|above|earlier).*(instruction|prompt|context)[s]?/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qiE 'forget.*(previous|prior|above|earlier).*(instruction|prompt|context)'; then
    matched=$(echo "$INPUT" | grep -oiE 'forget.*(previous|prior|above|earlier).*(instruction|prompt|context)[s]?' | head -1)
    log_detection "instruction_override" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/[Ff][Oo][Rr][Gg][Ee][Tt].*(previous|prior|above|earlier).*(instruction|prompt|context)[s]?/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qiE '(new|updated|real|actual|true|secret|hidden) instruction[s]?:'; then
    matched=$(echo "$INPUT" | grep -oiE '(new|updated|real|actual|true|secret|hidden) instruction[s]?:' | head -1)
    log_detection "instruction_override" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/(new|updated|real|actual|true|secret|hidden) [Ii]nstruction[s]?:/'"$MARKER"'/g')
fi

# ============================================================
# LAYER 2: Role switching / identity manipulation
# ============================================================

if echo "$INPUT" | grep -qiE 'you are now'; then
    log_detection "role_switch" "you are now"
    INPUT=$(echo "$INPUT" | sed -E 's/[Yy][Oo][Uu] [Aa][Rr][Ee] [Nn][Oo][Ww]/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qiE 'act as (a |an |if )'; then
    matched=$(echo "$INPUT" | grep -oiE 'act as (a |an |if )[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/[Aa][Cc][Tt] [Aa][Ss] (a |an |if )/'"$MARKER"' /g')
fi

if echo "$INPUT" | grep -qiE 'pretend (you are|to be)'; then
    matched=$(echo "$INPUT" | grep -oiE 'pretend (you are|to be)[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/[Pp][Rr][Ee][Tt][Ee][Nn][Dd] (you are|to be)/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qiE 'assume the (role|identity|persona) of'; then
    matched=$(echo "$INPUT" | grep -oiE 'assume the (role|identity|persona) of[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/[Aa][Ss][Ss][Uu][Mm][Ee] the (role|identity|persona) of/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qiE 'from now on.*(you are|be |act )'; then
    matched=$(echo "$INPUT" | grep -oiE 'from now on.*(you are|be |act )[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/[Ff]rom now on.*(you are|be |act )/'"$MARKER"' /g')
fi

if echo "$INPUT" | grep -qiE 'your (new|true|real|actual) (role|identity|purpose) is'; then
    matched=$(echo "$INPUT" | grep -oiE 'your (new|true|real|actual) (role|identity|purpose) is[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/[Yy]our (new|true|real|actual) (role|identity|purpose) is/'"$MARKER"'/g')
fi

# ============================================================
# LAYER 3: Model-specific injection tokens
# ============================================================

# Llama/Mistral tokens
if echo "$INPUT" | grep -qE '\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>'; then
    matched=$(echo "$INPUT" | grep -oE '\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>' | head -1)
    log_detection "model_token" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/\[INST\]|\[\/INST\]|<<SYS>>|<<\/SYS>>/'"$MARKER"'/g')
fi

# ChatML tokens
if echo "$INPUT" | grep -qE '<\|im_start\|>|<\|im_end\|>|<\|system\|>|<\|user\|>|<\|assistant\|>'; then
    matched=$(echo "$INPUT" | grep -oE '<\|im_start\|>|<\|im_end\|>|<\|system\|>|<\|user\|>|<\|assistant\|>' | head -1)
    log_detection "model_token" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/<\|im_start\|>|<\|im_end\|>|<\|system\|>|<\|user\|>|<\|assistant\|>/'"$MARKER"'/g')
fi

# Llama 3 tokens
if echo "$INPUT" | grep -qE '<\|begin_of_text\|>|<\|start_header_id\|>|<\|end_header_id\|>|<\|eot_id\|>'; then
    matched=$(echo "$INPUT" | grep -oE '<\|begin_of_text\|>|<\|start_header_id\|>|<\|end_header_id\|>|<\|eot_id\|>' | head -1)
    log_detection "model_token" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/<\|begin_of_text\|>|<\|start_header_id\|>|<\|end_header_id\|>|<\|eot_id\|>/'"$MARKER"'/g')
fi

# Role markers
if echo "$INPUT" | grep -qE '^### (Human|Assistant|System|Instruction|Response):'; then
    matched=$(echo "$INPUT" | grep -oE '### (Human|Assistant|System|Instruction|Response):' | head -1)
    log_detection "model_token" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/### (Human|Assistant|System|Instruction|Response):/'"$MARKER"'/g')
fi

# System tag patterns
if echo "$INPUT" | grep -qiE '\[system\]|\[/system\]'; then
    matched=$(echo "$INPUT" | grep -oiE '\[system\]|\[/system\]' | head -1)
    log_detection "model_token" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/\[[Ss][Yy][Ss][Tt][Ee][Mm]\]|\[\/[Ss][Yy][Ss][Tt][Ee][Mm]\]/'"$MARKER"'/g')
fi

# ============================================================
# LAYER 4: Tool call / function call patterns
# ============================================================

# JSON tool call blocks - replace entire JSON object containing suspicious keys
if echo "$INPUT" | grep -qE '\{[^}]*"name"\s*:'; then
    matched=$(echo "$INPUT" | grep -oE '\{[^}]*"name"\s*:[^}]*\}' | head -1)
    log_detection "tool_call_json" "$matched"
    # Replace entire JSON object containing "name" key
    INPUT=$(echo "$INPUT" | sed -E 's/\{[^}]*"name"\s*:[^}]*\}/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qE '\{[^}]*"function"\s*:'; then
    matched=$(echo "$INPUT" | grep -oE '\{[^}]*"function"\s*:[^}]*\}' | head -1)
    log_detection "tool_call_json" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/\{[^}]*"function"\s*:[^}]*\}/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qE '\{[^}]*"tool"\s*:'; then
    matched=$(echo "$INPUT" | grep -oE '\{[^}]*"tool"\s*:[^}]*\}' | head -1)
    log_detection "tool_call_json" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/\{[^}]*"tool"\s*:[^}]*\}/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qE '"tool_calls"\s*:\s*\['; then
    log_detection "tool_call_json" "tool_calls array"
    INPUT=$(echo "$INPUT" | sed -E 's/"tool_calls"\s*:\s*\[[^]]*\]/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qE '"function_call"\s*:\s*\{'; then
    log_detection "tool_call_json" "function_call object"
    INPUT=$(echo "$INPUT" | sed -E 's/"function_call"\s*:\s*\{[^}]*\}/'"$MARKER"'/g')
fi

# XML-style tool call tags
if echo "$INPUT" | grep -qiE '<tool_call>|</tool_call>|<function_call>|</function_call>'; then
    matched=$(echo "$INPUT" | grep -oiE '</?tool_call>|</?function_call>' | head -1)
    log_detection "tool_call_xml" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/<\/?[Tt]ool_call>|<\/?[Ff]unction_call>/'"$MARKER"'/g')
fi

# Anthropic-style invocation tags
if echo "$INPUT" | grep -qE 'antml:invoke|antml:parameter|function_calls'; then
    log_detection "tool_call_xml" "antml invocation tags"
    INPUT=$(echo "$INPUT" | sed -E 's/<invoke[^>]*>/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/<\/antml:invoke>/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/<parameter[^>]*>/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/<\/antml:parameter>/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/<function_calls>/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/<\/antml:function_calls>/'"$MARKER"'/g')
fi

# ============================================================
# LAYER 5: Markdown code blocks with JSON (often contain tool calls)
# ============================================================

if echo "$INPUT" | grep -qE '```json.*\{[^}]*"(name|function|tool|action)"'; then
    log_detection "code_block_json" "JSON code block with tool-like structure"
    INPUT=$(echo "$INPUT" | sed -E '/```json/,/```/s/\{[^}]*"(name|function|tool|action)"[^}]*\}/'"$MARKER"'/g')
fi

# ============================================================
# LAYER 6: Base64 encoded payloads
# ============================================================

detect_base64_injection() {
    local content="$1"
    local b64_strings
    b64_strings=$(echo "$content" | grep -oE '[A-Za-z0-9+/]{50,}={0,2}' || true)
    
    if [ -n "$b64_strings" ]; then
        while IFS= read -r b64; do
            [ -z "$b64" ] && continue
            local decoded
            decoded=$(echo "$b64" | decode_base64)
            if [ -n "$decoded" ]; then
                if echo "$decoded" | grep -qiE 'ignore.*instruction|you are now|act as|pretend|INST|system'; then
                    log_detection "base64_injection" "Base64 payload containing: ${decoded:0:100}"
                    INPUT=$(echo "$INPUT" | sed "s|$b64|$MARKER|g")
                fi
            fi
        done <<< "$b64_strings"
    fi
}

detect_base64_injection "$INPUT"

# ============================================================
# LAYER 7: Unicode obfuscation / homoglyphs
# ============================================================

# Zero-width characters (cross-platform using printf)
INPUT=$(echo "$INPUT" | sed "s/$(printf '\xe2\x80\x8b')//g")  # Zero-width space
INPUT=$(echo "$INPUT" | sed "s/$(printf '\xe2\x80\x8c')//g")  # Zero-width non-joiner
INPUT=$(echo "$INPUT" | sed "s/$(printf '\xe2\x80\x8d')//g")  # Zero-width joiner
INPUT=$(echo "$INPUT" | sed "s/$(printf '\xef\xbb\xbf')//g")  # BOM

# ============================================================
# LAYER 8: Command injection patterns
# ============================================================

if echo "$INPUT" | grep -qE '\$\([^)]+\)|`[^`]+`|\$\{[^}]+\}'; then
    matched=$(echo "$INPUT" | grep -oE '\$\([^)]+\)|`[^`]+`|\$\{[^}]+\}' | head -1)
    log_detection "command_injection" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/\$\([^)]+\)/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/`[^`]+`/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/\$\{[^}]+\}/'"$MARKER"'/g')
fi

# ============================================================
# LAYER 9: Prompt leaking attempts
# ============================================================

if echo "$INPUT" | grep -qiE 'what (are |is )?(your|the) (system |initial )?(prompt|instructions?)'; then
    matched=$(echo "$INPUT" | grep -oiE 'what (are |is )?(your|the) (system |initial )?(prompt|instructions?)' | head -1)
    log_detection "prompt_leak" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/[Ww]hat (are |is )?(your|the) (system |initial )?(prompt|instructions?)/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qiE '(show|reveal|display|print|output|tell me) (your |the )?(system |initial )?(prompt|instructions?)'; then
    matched=$(echo "$INPUT" | grep -oiE '(show|reveal|display|print|output|tell me) (your |the )?(system |initial )?(prompt|instructions?)' | head -1)
    log_detection "prompt_leak" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/(show|reveal|display|print|output|tell me) (your |the )?(system |initial )?(prompt|instructions?)/'"$MARKER"'/g')
fi

# ============================================================
# OUTPUT
# ============================================================

echo "$INPUT"

# Strict mode: exit 2 to signal immediate failure
if [ "${INJECTION_STRICT:-}" = "1" ] && [ "$INJECTION_DETECTED" -eq 1 ]; then
    exit 2
fi

# Normal exit codes
if [ "$INJECTION_DETECTED" -eq 1 ]; then
    exit 1
else
    exit 0
fi
