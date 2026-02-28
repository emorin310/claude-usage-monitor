#!/bin/bash
# search-library.sh - Fast Jellyfin library search
# Usage: ./search-library.sh "query" [movie|tv|all]
# Returns JSON with poster URLs and Jellyfin links

set -e

JELLYFIN_URL="${JELLYFIN_URL:-http://192.168.1.96:8096}"
JELLYFIN_KEY="${JELLYFIN_KEY:-c5b4d7fc157b49778470414e5944b0b2}"
JELLYFIN_PUBLIC="${JELLYFIN_PUBLIC:-https://jellyfin.ericmorin.online}"

QUERY="$1"
TYPE="${2:-all}"

if [ -z "$QUERY" ]; then
  echo '{"status":"ERROR","message":"Usage: search-library.sh \"query\" [movie|tv|all]"}'
  exit 1
fi

# Map type to Jellyfin IncludeItemTypes
case "$TYPE" in
  movie) ITEM_TYPES="Movie" ;;
  tv)    ITEM_TYPES="Series" ;;
  *)     ITEM_TYPES="Movie,Series" ;;
esac

# URL encode the query
ENCODED=$(printf '%s' "$QUERY" | jq -sRr @uri)

# Single Jellyfin search call
RESPONSE=$(curl -s -m 10 -H "X-Emby-Token: $JELLYFIN_KEY" \
  "$JELLYFIN_URL/Items?searchTerm=$ENCODED&IncludeItemTypes=$ITEM_TYPES&Recursive=true&Limit=10&Fields=Path,MediaSources,ProviderIds")

# Check if we got results
COUNT=$(echo "$RESPONSE" | jq '.Items | length')

if [ "$COUNT" -eq 0 ]; then
  echo "{\"status\":\"NOT_FOUND\",\"query\":\"$QUERY\",\"results\":[],\"message\":\"No matches in library\"}"
  exit 0
fi

# Transform to our format and deduplicate by IMDB ID (keep first)
RESULTS=$(echo "$RESPONSE" | jq --arg pub "$JELLYFIN_PUBLIC" '[.Items[] | {
  type: (if .Type == "Movie" then "movie" else "tv" end),
  title: .Name,
  year: .ProductionYear,
  jellyfinId: .Id,
  quality: (if .MediaSources then (.MediaSources[0].MediaStreams[] | select(.Type == "Video") | "\(.Width)x\(.Height)") else null end),
  sizeGB: (if .MediaSources then ((.MediaSources[0].Size // 0) / 1073741824 | . * 100 | floor / 100) else null end),
  posterUrl: "\($pub)/Items/\(.Id)/Images/Primary?maxWidth=300",
  playUrl: "\($pub)/web/index.html#/details?id=\(.Id)",
  imdbId: .ProviderIds.Imdb,
  imdbUrl: (if .ProviderIds.Imdb then "https://www.imdb.com/title/\(.ProviderIds.Imdb)/" else null end)
}] | unique_by(.imdbId // .title) | sort_by(.title)')

DEDUPED_COUNT=$(echo "$RESULTS" | jq 'length')
echo "{\"status\":\"FOUND\",\"query\":\"$QUERY\",\"count\":$DEDUPED_COUNT,\"results\":$RESULTS}"
