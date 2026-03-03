#!/bin/bash
# model-switch.sh - Smart model switching based on task type
# Usage: ./model-switch.sh <task-type> [command...]

TASK_TYPE="$1"
shift

case "$TASK_TYPE" in
    "routine"|"heartbeat"|"status"|"simple")
        MODEL="haiku"
        ;;
    "research"|"complex"|"reasoning"|"main")
        MODEL="sonnet"
        ;;
    "critical"|"deep"|"major"|"emergency")
        MODEL="opus"
        ;;
    *)
        echo "Usage: $0 {routine|research|critical} [command...]"
        echo "Models: routine->haiku, research->sonnet, critical->opus"
        exit 1
        ;;
esac

echo "🎯 Switching to $MODEL model for $TASK_TYPE task..."

# Switch model via OpenClaw CLI
openclaw agent set-model "$MODEL"

# Execute remaining command if provided
if [ $# -gt 0 ]; then
    echo "▶️ Executing: $*"
    "$@"
fi