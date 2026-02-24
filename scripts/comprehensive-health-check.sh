#!/bin/bash
# Comprehensive health check for Magi - can be called by cron or heartbeat

set -e

LOG_FILE="/home/magi/clawd/logs/comprehensive-health.log"
STATE_FILE="/home/magi/clawd/memory/health-state.json"

mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$STATE_FILE")"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Initialize state file if it doesn't exist
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" << 'EOF'
{
  "lastChecks": {
    "email": null,
    "calendar": null,
    "todoist": null,
    "system": null,
    "homeassistant": null
  },
  "lastAlerts": {},
  "counters": {
    "emailChecks": 0,
    "calendarChecks": 0,
    "todoistChecks": 0
  }
}
EOF
fi

CURRENT_TIME=$(date '+%s')
CHECK_TYPE="${1:-all}"  # all, email, calendar, todoist, system, homeassistant

log "Starting comprehensive health check (type: $CHECK_TYPE)..."

# Function to update state
update_state() {
    local check_type="$1"
    jq ".lastChecks.$check_type = $CURRENT_TIME" "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
    jq ".counters.${check_type}Checks += 1" "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# Function to check if we should run a specific check (to avoid spam)
should_check() {
    local check_type="$1"
    local min_interval="$2"  # in seconds
    
    local last_check=$(jq -r ".lastChecks.$check_type" "$STATE_FILE")
    
    if [ "$last_check" == "null" ]; then
        return 0  # Never checked before
    fi
    
    local time_since=$((CURRENT_TIME - last_check))
    if [ $time_since -ge $min_interval ]; then
        return 0  # Enough time has passed
    fi
    
    return 1  # Too soon
}

# Store results
RESULTS_FILE="/tmp/health_check_results_$$"
echo "[]" > "$RESULTS_FILE"

# Email check (every 30 minutes)
if [ "$CHECK_TYPE" == "all" ] || [ "$CHECK_TYPE" == "email" ]; then
    if should_check "email" 1800; then  # 30 minutes
        log "Checking email..."
        update_state "email"
        
        # This will be implemented by calling Magi with specific email check task
        echo '{"type":"email","status":"pending","message":"Email check scheduled"}' | jq '.' >> "$RESULTS_FILE"
    else
        log "Skipping email check (too recent)"
    fi
fi

# Calendar check (every 30 minutes) 
if [ "$CHECK_TYPE" == "all" ] || [ "$CHECK_TYPE" == "calendar" ]; then
    if should_check "calendar" 1800; then  # 30 minutes
        log "Checking calendar..."
        update_state "calendar"
        
        echo '{"type":"calendar","status":"pending","message":"Calendar check scheduled"}' | jq '.' >> "$RESULTS_FILE"
    else
        log "Skipping calendar check (too recent)"
    fi
fi

# Todoist check (every 15 minutes during work hours)
if [ "$CHECK_TYPE" == "all" ] || [ "$CHECK_TYPE" == "todoist" ]; then
    HOUR=$(date '+%H')
    if [ $HOUR -ge 8 ] && [ $HOUR -le 18 ]; then  # Work hours
        if should_check "todoist" 900; then  # 15 minutes
            log "Checking Todoist..."
            update_state "todoist"
            
            # Run the existing Todoist check
            if /home/magi/clawd/scripts/check-todoist.sh > /tmp/todoist_result.json; then
                echo '{"type":"todoist","status":"completed","data":"'$(cat /tmp/todoist_result.json)'"}' | jq '.' >> "$RESULTS_FILE"
            else
                echo '{"type":"todoist","status":"error","message":"Todoist check failed"}' | jq '.' >> "$RESULTS_FILE"
            fi
        fi
    fi
fi

# System check (every 2 hours)
if [ "$CHECK_TYPE" == "all" ] || [ "$CHECK_TYPE" == "system" ]; then
    if should_check "system" 7200; then  # 2 hours
        log "Checking system health..."
        update_state "system"
        
        # Basic system checks
        DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
        MEMORY_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
        LOAD_AVG=$(uptime | awk '{print $10}' | sed 's/,//')
        
        SYSTEM_ALERTS=()
        
        if [ $DISK_USAGE -gt 85 ]; then
            SYSTEM_ALERTS+=("Disk usage high: ${DISK_USAGE}%")
        fi
        
        if [ $(echo "$MEMORY_USAGE > 90" | bc) -eq 1 ]; then
            SYSTEM_ALERTS+=("Memory usage high: ${MEMORY_USAGE}%")
        fi
        
        if [ ${#SYSTEM_ALERTS[@]} -gt 0 ]; then
            ALERTS_JSON=$(printf '%s\n' "${SYSTEM_ALERTS[@]}" | jq -R . | jq -s .)
            echo "{\"type\":\"system\",\"status\":\"alert\",\"alerts\":$ALERTS_JSON}" >> "$RESULTS_FILE"
        else
            echo '{"type":"system","status":"ok","message":"System healthy"}' >> "$RESULTS_FILE"
        fi
    fi
fi

# Compile final results
FINAL_RESULTS=$(jq -s '.' "$RESULTS_FILE")
rm "$RESULTS_FILE"

# Output results for consumption by Magi
echo "$FINAL_RESULTS" > "/tmp/health_check_final_results.json"

log "Health check completed"
exit 0