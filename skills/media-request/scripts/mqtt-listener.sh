#!/bin/bash
# mqtt-listener.sh - Listen for incoming media requests from Magi
# Run as daemon or via systemd
# Receives: {"from":"magi","payload":{"action":"request_movie",...}}

MQTT_HOST="${MQTT_HOST:-192.168.1.151}"
MQTT_PORT="${MQTT_PORT:-1883}"
MQTT_USER="${MQTT_USER:-mqtt}"
MQTT_PASS="${MQTT_PASS:-letx}"
MARVIN_TOPIC="${MARVIN_TOPIC:-bots/marvin/inbox}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/../data/mqtt-listener.log"

log() {
  echo "[$(date -Iseconds)] $*" >> "$LOG_FILE"
}

handle_message() {
  local MSG="$1"
  log "Received: $MSG"
  
  # Extract payload
  PAYLOAD=$(echo "$MSG" | jq -r '.payload // empty')
  if [ -z "$PAYLOAD" ] || [ "$PAYLOAD" = "null" ]; then
    log "No payload in message"
    return
  fi
  
  ACTION=$(echo "$PAYLOAD" | jq -r '.action // empty')
  
  case "$ACTION" in
    request_movie)
      log "Processing movie request"
      RESULT=$("$SCRIPT_DIR/handle-request.sh" "$PAYLOAD" 2>&1)
      log "Result: $RESULT"
      
      # Send response back to sender
      FROM=$(echo "$MSG" | jq -r '.from // "unknown"')
      if [ "$FROM" = "magi" ]; then
        NOTIFY_RESULT=$("$SCRIPT_DIR/notify-magi.sh" "$RESULT" 2>&1)
        log "Notified Magi: $NOTIFY_RESULT"
      fi
      ;;
    check_status)
      log "Processing status check"
      RADARR_ID=$(echo "$PAYLOAD" | jq -r '.radarrId')
      RESULT=$("$SCRIPT_DIR/check-download.sh" "$RADARR_ID" 2>&1)
      log "Result: $RESULT"
      FROM=$(echo "$MSG" | jq -r '.from // "unknown"')
      if [ "$FROM" = "magi" ]; then
        NOTIFY_RESULT=$("$SCRIPT_DIR/notify-magi.sh" "$RESULT" 2>&1)
        log "Notified Magi: $NOTIFY_RESULT"
      fi
      ;;
    search)
      log "Processing library search"
      QUERY=$(echo "$PAYLOAD" | jq -r '.query')
      TYPE=$(echo "$PAYLOAD" | jq -r '.type // "all"')
      RESULT=$("$SCRIPT_DIR/search-library.sh" "$QUERY" "$TYPE" 2>&1)
      log "Result: $RESULT"
      FROM=$(echo "$MSG" | jq -r '.from // "unknown"')
      [ "$FROM" = "magi" ] && "$SCRIPT_DIR/notify-magi.sh" "$RESULT" 2>/dev/null
      ;;
    stats)
      log "Processing library stats"
      RESULT=$("$SCRIPT_DIR/library-stats.sh" 2>&1)
      log "Result: $RESULT"
      FROM=$(echo "$MSG" | jq -r '.from // "unknown"')
      [ "$FROM" = "magi" ] && "$SCRIPT_DIR/notify-magi.sh" "$RESULT" 2>/dev/null
      ;;
    search_tmdb)
      log "Processing TMDB search"
      QUERY=$(echo "$PAYLOAD" | jq -r '.query')
      TYPE=$(echo "$PAYLOAD" | jq -r '.type // "movie"')
      RESULT=$("$SCRIPT_DIR/search-tmdb.sh" "$QUERY" "$TYPE" 2>&1)
      log "Result: $RESULT"
      FROM=$(echo "$MSG" | jq -r '.from // "unknown"')
      [ "$FROM" = "magi" ] && "$SCRIPT_DIR/notify-magi.sh" "$RESULT" 2>/dev/null
      ;;
    quickconnect)
      log "Processing Quick Connect authorization"
      QC_CODE=$(echo "$PAYLOAD" | jq -r '.code')
      RESULT=$("$SCRIPT_DIR/jellyfin-quickconnect.sh" "$QC_CODE" 2>&1)
      log "Result: $RESULT"
      FROM=$(echo "$MSG" | jq -r '.from // "unknown"')
      [ "$FROM" = "magi" ] && "$SCRIPT_DIR/notify-magi.sh" "$RESULT" 2>/dev/null
      ;;
    weekly_stats)
      log "Processing weekly stats request"
      DAYS=$(echo "$PAYLOAD" | jq -r '.days // 7')
      RESULT=$("$SCRIPT_DIR/weekly-stats.sh" "$DAYS" 2>&1)
      log "Result: $RESULT"
      FROM=$(echo "$MSG" | jq -r '.from // "unknown"')
      [ "$FROM" = "magi" ] && "$SCRIPT_DIR/notify-magi.sh" "$RESULT" 2>/dev/null
      ;;
    ping)
      log "Processing ping from $FROM"
      RESULT='{"status":"pong","from":"marvin","message":"I hear you!"}'
      [ "$FROM" = "magi" ] && "$SCRIPT_DIR/notify-magi.sh" "$RESULT" 2>/dev/null
      ;;
    *)
      log "Unknown action: $ACTION - routing to Gemini"
      RESULT=$("$SCRIPT_DIR/llm-handler.sh" "$MSG" 2>&1)
      log "Gemini result: $RESULT"
      FROM=$(echo "$MSG" | jq -r '.from // "unknown"')
      [ "$FROM" = "magi" ] && "$SCRIPT_DIR/notify-magi.sh" "$RESULT" 2>/dev/null
      ;;
  esac
}

log "Starting MQTT listener on $MARVIN_TOPIC"

# Subscribe and process messages
mosquitto_sub -h "$MQTT_HOST" -p "$MQTT_PORT" -u "$MQTT_USER" -P "$MQTT_PASS" \
  -t "$MARVIN_TOPIC" | while read -r line; do
  handle_message "$line"
done
