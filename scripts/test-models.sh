#!/bin/bash
# Daily model health check - tests all configured models

MODELS=(
  "anthropic/claude-sonnet-4-5-20250929"
  "anthropic/claude-opus-4-5"
  "deepseek/deepseek-reasoner"
  "groq/llama-3.3-70b-versatile"
  "google/gemini-2.0-flash"
  "moonshot/moonshot-v1-128k"
  "ollama/qwen2.5:14b"
)

LOG_FILE="$HOME/clawd/logs/model-health.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
RESULTS_FILE="$HOME/clawd/data/model-health-$(date +%Y-%m-%d).json"

echo "[$TIMESTAMP] Starting model health check" >> "$LOG_FILE"

# Create results JSON
echo "{" > "$RESULTS_FILE"
echo "  \"timestamp\": \"$TIMESTAMP\"," >> "$RESULTS_FILE"
echo "  \"tests\": {" >> "$RESULTS_FILE"

FIRST=true
for MODEL in "${MODELS[@]}"; do
  echo "[$TIMESTAMP] Testing $MODEL..." >> "$LOG_FILE"
  
  # Add comma separator except for first entry
  if [ "$FIRST" = false ]; then
    echo "," >> "$RESULTS_FILE"
  fi
  FIRST=false
  
  # Test with simple prompt via sessions_spawn
  RESULT=$(curl -s -X POST "http://localhost:18790/api/sessions/spawn" \
    -H "Authorization: Bearer ec788e78c55feb2f970e14a41ea10a2d656155e650ae3f25" \
    -H "Content-Type: application/json" \
    -d "{
      \"task\": \"Respond with exactly: OK\",
      \"model\": \"$MODEL\",
      \"cleanup\": \"delete\",
      \"timeoutSeconds\": 30
    }" 2>&1)
  
  if echo "$RESULT" | grep -q '"status":"accepted"'; then
    echo "    \"$MODEL\": { \"status\": \"ok\", \"tested\": \"$TIMESTAMP\" }" >> "$RESULTS_FILE"
    echo "[$TIMESTAMP] ✅ $MODEL: OK" >> "$LOG_FILE"
  else
    echo "    \"$MODEL\": { \"status\": \"failed\", \"tested\": \"$TIMESTAMP\", \"error\": \"spawn failed\" }" >> "$RESULTS_FILE"
    echo "[$TIMESTAMP] ❌ $MODEL: FAILED" >> "$LOG_FILE"
  fi
  
  sleep 2  # Rate limit protection
done

echo "" >> "$RESULTS_FILE"
echo "  }" >> "$RESULTS_FILE"
echo "}" >> "$RESULTS_FILE"

# Count failures
FAILURES=$(grep '"status": "failed"' "$RESULTS_FILE" | wc -l | tr -d ' ')

echo "[$TIMESTAMP] Health check complete: $FAILURES failures" >> "$LOG_FILE"

# Alert if >2 models failed
if [ "$FAILURES" -gt 2 ]; then
  echo "⚠️ Model health check: $FAILURES models failed!" >> "$LOG_FILE"
  # Could add Telegram notification here
fi

exit 0
