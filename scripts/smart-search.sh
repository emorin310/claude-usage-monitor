#!/bin/bash
# smart-search.sh - Fuzzy search with variations
# Usage: ./smart-search.sh "query"
# Tries multiple variations and returns best matches

QUERY="$1"
SEARCH_SCRIPT="/Users/eric/clawd-magi/scripts/scripts/search-library.sh"

if [ -z "$QUERY" ]; then
  echo '{"status":"ERROR","message":"Usage: smart-search.sh \"movie name\""}'
  exit 1
fi

# Function to search and check results
search() {
  local q="$1"
  local result=$("$SEARCH_SCRIPT" "$q" 2>/dev/null)
  local status=$(echo "$result" | jq -r '.status // "ERROR"')
  if [ "$status" = "FOUND" ]; then
    echo "$result"
    return 0
  fi
  return 1
}

# Try exact query first
if result=$(search "$QUERY"); then
  echo "$result"
  exit 0
fi

# Generate variations
VARIATIONS=()

# Remove common words
CLEAN=$(echo "$QUERY" | sed -E 's/\b(the|a|an|and|of|at)\b//gi' | tr -s ' ' | xargs)
[ -n "$CLEAN" ] && [ "$CLEAN" != "$QUERY" ] && VARIATIONS+=("$CLEAN")

# Try each word separately (for multi-word queries)
for word in $QUERY; do
  [ ${#word} -gt 3 ] && VARIATIONS+=("$word")
done

# Try first two words
FIRST_TWO=$(echo "$QUERY" | awk '{print $1, $2}' | xargs)
[ -n "$FIRST_TWO" ] && [ "$FIRST_TWO" != "$QUERY" ] && VARIATIONS+=("$FIRST_TWO")

# Try last two words
LAST_TWO=$(echo "$QUERY" | awk '{print $(NF-1), $NF}' | xargs)
[ -n "$LAST_TWO" ] && [ "$LAST_TWO" != "$FIRST_TWO" ] && VARIATIONS+=("$LAST_TWO")

# Search variations
ALL_RESULTS='{"status":"NOT_FOUND","query":"'"$QUERY"'","variations_tried":[],"results":[]}'

for var in "${VARIATIONS[@]}"; do
  if result=$(search "$var"); then
    # Found something! Add to results
    count=$(echo "$result" | jq '.count // 0')
    results=$(echo "$result" | jq '.results // []')
    
    # Merge results
    ALL_RESULTS=$(echo "$ALL_RESULTS" | jq --arg var "$var" --argjson res "$results" '
      .status = "FOUND" |
      .variations_tried += [$var] |
      .results += $res |
      .results = (.results | unique_by(.title))
    ')
  else
    ALL_RESULTS=$(echo "$ALL_RESULTS" | jq --arg var "$var" '.variations_tried += [$var]')
  fi
done

# Update count
ALL_RESULTS=$(echo "$ALL_RESULTS" | jq '.count = (.results | length)')

echo "$ALL_RESULTS"
