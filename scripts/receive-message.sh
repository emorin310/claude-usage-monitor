#!/bin/bash
# Simple message receiver - writes incoming messages to a queue file
QUEUE_FILE="$HOME/clawd/memory/incoming-messages.jsonl"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Read POST body from stdin
read -r BODY

# Append to queue
echo "{\"timestamp\": \"$TIMESTAMP\", \"message\": $BODY}" >> "$QUEUE_FILE"
echo "OK"
