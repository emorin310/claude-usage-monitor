#!/bin/bash
# MQTT Listener for Magi
# Listens to bots/magi/inbox and bots/broadcast

LOG_FILE="/Users/eric/clawd-magi/memory/mqtt-inbox.log"
STATE_FILE="/Users/eric/clawd-magi/memory/mqtt-last-message.json"

echo "[$(date -Iseconds)] MQTT Listener started" >> "$LOG_FILE"

# Use %j format for JSON output
mosquitto_sub -h 192.168.1.151 -u mqtt -P letx \
  -t "bots/magi/inbox" \
  -t "bots/broadcast" \
  -F '{"recv_topic":"%t","recv_time":"%I","payload":%p}' | while read -r LINE; do
    TIMESTAMP=$(date -Iseconds)
    
    # Log raw JSON
    echo "===== [$TIMESTAMP] =====" >> "$LOG_FILE"
    echo "$LINE" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # Write state file
    echo "$LINE" > "$STATE_FILE"
    
    echo "[$TIMESTAMP] Message received"
done
