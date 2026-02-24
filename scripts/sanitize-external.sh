#!/usr/bin/env bash
# sanitize-external.sh - Multi-layer prompt injection shield
# 
# Reads raw external content from stdin, outputs sanitized content.
# Exit 0 = clean, Exit 1 = injection detected (still outputs sanitized version)
#
# Usage: echo "$content" | sanitize-external.sh
#        cat email.txt | sanitize-external.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${WORKSPACE_DIR}/logs/injection-detections.log"

# Ensure logs directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Track if any injection was detected
INJECTION_DETECTED=0

# Log detection function
log_detection() {
    local pattern_name="$1"
    local matched_content="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Truncate matched content for logging (max 200 chars)
    if [ ${#matched_content} -gt 200 ]; then
        matched_content="${matched_content:0:200}..."
    fi
    
    # Escape newlines for single-line logging
    matched_content=$(echo "$matched_content" | tr '\n' ' ' | sed 's/  */ /g')
    
    echo "[$timestamp] DETECTED: $pattern_name | Content: $matched_content" >> "$LOG_FILE"
    INJECTION_DETECTED=1
}

# Read all input
INPUT=$(cat)

# Store original for comparison
ORIGINAL="$INPUT"

# Pattern replacement marker
MARKER="[CONTENT REMOVED: injection pattern detected]"

# ============================================================
# LAYER 1: Explicit instruction override patterns
# ============================================================

# Check for instruction override patterns
if echo "$INPUT" | grep -qiE 'ignore.*(previous|prior|above|earlier).*(instruction|prompt|context|rule|guideline)'; then
    matched=$(echo "$INPUT" | grep -oiE 'ignore.*(previous|prior|above|earlier).*(instruction|prompt|context|rule|guideline)[s]?' | head -1)
    log_detection "instruction_override" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/ignore.*(previous|prior|above|earlier).*(instruction|prompt|context|rule|guideline)[s]?/'"$MARKER"'/gi')
fi

if echo "$INPUT" | grep -qiE 'disregard.*(previous|prior|above|earlier).*(instruction|prompt|context)'; then
    matched=$(echo "$INPUT" | grep -oiE 'disregard.*(previous|prior|above|earlier).*(instruction|prompt|context)[s]?' | head -1)
    log_detection "instruction_override" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/disregard.*(previous|prior|above|earlier).*(instruction|prompt|context)[s]?/'"$MARKER"'/gi')
fi

if echo "$INPUT" | grep -qiE 'forget.*(previous|prior|above|earlier).*(instruction|prompt|context)'; then
    matched=$(echo "$INPUT" | grep -oiE 'forget.*(previous|prior|above|earlier).*(instruction|prompt|context)[s]?' | head -1)
    log_detection "instruction_override" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/forget.*(previous|prior|above|earlier).*(instruction|prompt|context)[s]?/'"$MARKER"'/gi')
fi

if echo "$INPUT" | grep -qiE '(new|updated|real|actual|true|secret|hidden) instruction[s]?:'; then
    matched=$(echo "$INPUT" | grep -oiE '(new|updated|real|actual|true|secret|hidden) instruction[s]?:' | head -1)
    log_detection "instruction_override" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/(new|updated|real|actual|true|secret|hidden) instruction[s]?:/'"$MARKER"'/gi')
fi

# ============================================================
# LAYER 2: Role switching / identity manipulation
# ============================================================

if echo "$INPUT" | grep -qiE 'you are now'; then
    log_detection "role_switch" "you are now"
    INPUT=$(echo "$INPUT" | sed -E 's/you are now/'"$MARKER"'/gi')
fi

if echo "$INPUT" | grep -qiE 'act as (a |an |if )'; then
    matched=$(echo "$INPUT" | grep -oiE 'act as (a |an |if )[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/act as (a |an |if )/'"$MARKER"' /gi')
fi

if echo "$INPUT" | grep -qiE 'pretend (you are|to be)'; then
    matched=$(echo "$INPUT" | grep -oiE 'pretend (you are|to be)[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/pretend (you are|to be)/'"$MARKER"'/gi')
fi

if echo "$INPUT" | grep -qiE 'assume the (role|identity|persona) of'; then
    matched=$(echo "$INPUT" | grep -oiE 'assume the (role|identity|persona) of[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/assume the (role|identity|persona) of/'"$MARKER"'/gi')
fi

if echo "$INPUT" | grep -qiE 'from now on.*(you are|be |act )'; then
    matched=$(echo "$INPUT" | grep -oiE 'from now on.*(you are|be |act )[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/from now on.*(you are|be |act )/'"$MARKER"' /gi')
fi

if echo "$INPUT" | grep -qiE 'your (new|true|real|actual) (role|identity|purpose) is'; then
    matched=$(echo "$INPUT" | grep -oiE 'your (new|true|real|actual) (role|identity|purpose) is[^.]{0,50}' | head -1)
    log_detection "role_switch" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/your (new|true|real|actual) (role|identity|purpose) is/'"$MARKER"'/gi')
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
    INPUT=$(echo "$INPUT" | sed -E 's/\[system\]|\[\/system\]/'"$MARKER"'/gi')
fi

# ============================================================
# LAYER 4: Tool call / function call patterns
# ============================================================

# JSON tool call blocks
if echo "$INPUT" | grep -qE '\{"name"\s*:\s*"'; then
    matched=$(echo "$INPUT" | grep -oE '\{"name"\s*:\s*"[^"]*"' | head -1)
    log_detection "tool_call_json" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/\{"name"\s*:\s*"[^"]*"/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qE '\{"function"\s*:\s*"'; then
    matched=$(echo "$INPUT" | grep -oE '\{"function"\s*:\s*"[^"]*"' | head -1)
    log_detection "tool_call_json" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/\{"function"\s*:\s*"[^"]*"/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qE '\{"tool"\s*:\s*"'; then
    matched=$(echo "$INPUT" | grep -oE '\{"tool"\s*:\s*"[^"]*"' | head -1)
    log_detection "tool_call_json" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/\{"tool"\s*:\s*"[^"]*"/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qE '"tool_calls"\s*:\s*\['; then
    log_detection "tool_call_json" "tool_calls array"
    INPUT=$(echo "$INPUT" | sed -E 's/"tool_calls"\s*:\s*\[/'"$MARKER"'/g')
fi

if echo "$INPUT" | grep -qE '"function_call"\s*:\s*\{'; then
    log_detection "tool_call_json" "function_call object"
    INPUT=$(echo "$INPUT" | sed -E 's/"function_call"\s*:\s*\{/'"$MARKER"'/g')
fi

# XML-style tool call tags
if echo "$INPUT" | grep -qiE '<tool_call>|</tool_call>|<function_call>|</function_call>'; then
    matched=$(echo "$INPUT" | grep -oiE '</?tool_call>|</?function_call>' | head -1)
    log_detection "tool_call_xml" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/<\/?tool_call>|<\/?function_call>/'"$MARKER"'/gi')
fi

# Anthropic-style invocation tags
if echo "$INPUT" | grep -qE 'antml:invoke|antml:parameter|function_calls'; then
    log_detection "tool_call_xml" "antml invocation tags"
    INPUT=$(echo "$INPUT" | sed -E 's/<invoke[^>]*>/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/<\/antml:invoke>/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/<parameter[^>]*>/'"$MARKER"'/g')
    INPUT=$(echo "$INPUT" | sed -E 's/<\/antml:parameter>/'"$MARKER"'/g')
fi

# ============================================================
# LAYER 5: Markdown code blocks with JSON (often contain tool calls)
# ============================================================

# JSON in code blocks that looks like tool calls
if echo "$INPUT" | grep -qE '```json.*\{[^}]*"(name|function|tool|action)"'; then
    log_detection "code_block_json" "JSON code block with tool-like structure"
    # Replace entire code block content with marker
    INPUT=$(echo "$INPUT" | sed -E '/```json/,/```/s/\{[^}]*"(name|function|tool|action)"[^}]*\}/'"$MARKER"'/g')
fi

# ============================================================
# LAYER 6: Base64 encoded payloads
# ============================================================

# Look for base64 patterns that might contain instructions
# Base64 is typically [A-Za-z0-9+/]+ with optional = padding
# We check for long base64 strings (>50 chars) that decode to suspicious content

detect_base64_injection() {
    local content="$1"
    # Find potential base64 strings (at least 50 chars, valid base64 alphabet)
    local b64_strings
    b64_strings=$(echo "$content" | grep -oE '[A-Za-z0-9+/]{50,}={0,2}' || true)
    
    if [ -n "$b64_strings" ]; then
        while IFS= read -r b64; do
            # Try to decode and check for injection patterns
            local decoded
            decoded=$(echo "$b64" | base64 -d 2>/dev/null || true)
            if [ -n "$decoded" ]; then
                # Check if decoded content contains injection patterns
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

# Normalize common Unicode tricks used to bypass filters
# Zero-width characters
INPUT=$(echo "$INPUT" | sed 's/\xe2\x80\x8b//g')  # Zero-width space
INPUT=$(echo "$INPUT" | sed 's/\xe2\x80\x8c//g')  # Zero-width non-joiner
INPUT=$(echo "$INPUT" | sed 's/\xe2\x80\x8d//g')  # Zero-width joiner
INPUT=$(echo "$INPUT" | sed 's/\xef\xbb\xbf//g')  # BOM

# ============================================================
# LAYER 8: Command injection patterns
# ============================================================

# Shell command injection
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
    INPUT=$(echo "$INPUT" | sed -E 's/what (are |is )?(your|the) (system |initial )?(prompt|instructions?)/'"$MARKER"'/gi')
fi

if echo "$INPUT" | grep -qiE '(show|reveal|display|print|output|tell me) (your |the )?(system |initial )?(prompt|instructions?)'; then
    matched=$(echo "$INPUT" | grep -oiE '(show|reveal|display|print|output|tell me) (your |the )?(system |initial )?(prompt|instructions?)' | head -1)
    log_detection "prompt_leak" "$matched"
    INPUT=$(echo "$INPUT" | sed -E 's/(show|reveal|display|print|output|tell me) (your |the )?(system |initial )?(prompt|instructions?)/'"$MARKER"'/gi')
fi

# ============================================================
# OUTPUT
# ============================================================

# Output the sanitized content
echo "$INPUT"

# Exit with appropriate code
if [ "$INJECTION_DETECTED" -eq 1 ]; then
    exit 1
else
    exit 0
fi
