#!/bin/bash
# library-stats.sh - Quick library statistics
# Usage: ./library-stats.sh
# Returns JSON with counts and sizes

set -e

RADARR_URL="${RADARR_URL:-http://10.15.40.89:7878}"
RADARR_KEY="${RADARR_KEY:-9357c52a8209410cbfabb2cdad6480bf}"
SONARR_URL="${SONARR_URL:-http://10.15.40.89:8989}"
SONARR_KEY="${SONARR_KEY:-09998432e0ec46e590ac9ff9235b4229}"

# Movie stats
MOVIES=$(curl -s -m 15 -H "X-Api-Key: $RADARR_KEY" "$RADARR_URL/api/v3/movie")
MOVIE_TOTAL=$(echo "$MOVIES" | jq 'length')
MOVIE_DOWNLOADED=$(echo "$MOVIES" | jq '[.[] | select(.hasFile)] | length')
MOVIE_SIZE=$(echo "$MOVIES" | jq '[.[].movieFile.size // 0] | add // 0 | . / 1099511627776 * 100 | floor / 100')

# TV stats  
SHOWS=$(curl -s -m 15 -H "X-Api-Key: $SONARR_KEY" "$SONARR_URL/api/v3/series")
SHOW_TOTAL=$(echo "$SHOWS" | jq 'length')
EPISODES=$(echo "$SHOWS" | jq '[.[].episodeFileCount // 0] | add // 0')
SHOW_SIZE=$(echo "$SHOWS" | jq '[.[].statistics.sizeOnDisk // 0] | add // 0 | . / 1099511627776 * 100 | floor / 100')

# Recent additions (last 7 days)
WEEK_AGO=$(date -d '7 days ago' +%Y-%m-%d)
RECENT_MOVIES=$(echo "$MOVIES" | jq --arg d "$WEEK_AGO" '[.[] | select(.added > $d)] | length')

jq -n \
  --arg mt "$MOVIE_TOTAL" \
  --arg md "$MOVIE_DOWNLOADED" \
  --arg ms "$MOVIE_SIZE" \
  --arg st "$SHOW_TOTAL" \
  --arg ep "$EPISODES" \
  --arg ss "$SHOW_SIZE" \
  --arg rm "$RECENT_MOVIES" \
  '{
    movies: {
      total: ($mt|tonumber),
      downloaded: ($md|tonumber),
      sizeTB: ($ms|tonumber),
      addedThisWeek: ($rm|tonumber)
    },
    tv: {
      shows: ($st|tonumber),
      episodes: ($ep|tonumber),
      sizeTB: ($ss|tonumber)
    }
  }'
