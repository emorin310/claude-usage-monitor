#!/bin/bash
# weekly-stats.sh - Get weekly watch/request stats for digest
# Usage: ./weekly-stats.sh [days]
# Returns JSON with watch history and request stats

set -e

JELLYFIN_URL="${JELLYFIN_URL:-http://192.168.1.96:8096}"
JELLYFIN_KEY="${JELLYFIN_KEY:-c5b4d7fc157b49778470414e5944b0b2}"
RADARR_URL="${RADARR_URL:-http://10.15.40.89:7878}"
RADARR_KEY="${RADARR_KEY:-9357c52a8209410cbfabb2cdad6480bf}"

DAYS="${1:-7}"
SINCE=$(date -d "$DAYS days ago" -Iseconds)

# Get Jellyfin playback activity
PLAYBACK=$(curl -s -m 30 "$JELLYFIN_URL/System/ActivityLog/Entries?limit=500&minDate=$SINCE" \
  -H "X-Emby-Token: $JELLYFIN_KEY" | \
  jq '[.Items[] | select(.Type == "VideoPlaybackStopped") | {
    user: (.Name | split(" has ")[0]),
    title: (.Name | capture("playing (?<t>.+) on") | .t),
    date: .Date,
    device: (.Name | split(" on ")[1] // "Unknown")
  }]')

# Count unique plays per title
WATCH_STATS=$(echo "$PLAYBACK" | jq 'group_by(.title) | map({
  title: .[0].title,
  plays: length,
  users: ([.[].user] | unique),
  lastWatched: (sort_by(.date) | last.date)
}) | sort_by(-.plays)')

# Get movies added this week from Radarr
WEEK_AGO=$(date -d "$DAYS days ago" +%Y-%m-%d)
ADDED_MOVIES=$(curl -s -m 15 -H "X-Api-Key: $RADARR_KEY" "$RADARR_URL/api/v3/movie" | \
  jq --arg d "$WEEK_AGO" '[.[] | select(.added > $d) | {
    title: .title,
    year: .year,
    added: .added,
    hasFile: .hasFile,
    quality: (.movieFile.quality.quality.name // null)
  }]')

# Summary stats
TOTAL_PLAYS=$(echo "$PLAYBACK" | jq 'length')
UNIQUE_TITLES=$(echo "$PLAYBACK" | jq '[.[].title] | unique | length')
UNIQUE_USERS=$(echo "$PLAYBACK" | jq '[.[].user] | unique | length')
MOVIES_ADDED=$(echo "$ADDED_MOVIES" | jq 'length')
MOVIES_DOWNLOADED=$(echo "$ADDED_MOVIES" | jq '[.[] | select(.hasFile)] | length')

jq -n \
  --arg days "$DAYS" \
  --arg since "$SINCE" \
  --argjson plays "$TOTAL_PLAYS" \
  --argjson titles "$UNIQUE_TITLES" \
  --argjson users "$UNIQUE_USERS" \
  --argjson added "$MOVIES_ADDED" \
  --argjson downloaded "$MOVIES_DOWNLOADED" \
  --argjson watchStats "$WATCH_STATS" \
  --argjson addedMovies "$ADDED_MOVIES" \
  '{
    period: {
      days: ($days|tonumber),
      since: $since
    },
    summary: {
      totalPlays: $plays,
      uniqueTitles: $titles,
      uniqueUsers: $users,
      moviesAdded: $added,
      moviesDownloaded: $downloaded
    },
    topWatched: ($watchStats | .[0:10]),
    recentlyAdded: ($addedMovies | .[0:10])
  }'
