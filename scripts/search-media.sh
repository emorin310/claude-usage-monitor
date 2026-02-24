#!/bin/bash
# search-media.sh - Search Jellyfin for movies AND TV shows
# Usage: ./search-media.sh "query" [movie|tv|all]

JELLYFIN_URL="${JELLYFIN_URL:-http://192.168.1.96:8096}"
JELLYFIN_KEY="${JELLYFIN_KEY:-c5b4d7fc157b49778470414e5944b0b2}"
JELLYFIN_PUBLIC="https://jellyfin.ericmorin.online"

QUERY="$1"
TYPE="${2:-all}"

if [ -z "$QUERY" ]; then
  echo '{"status":"ERROR","message":"Usage: search-media.sh \"query\" [movie|tv|all]"}'
  exit 1
fi

ENCODED=$(printf '%s' "$QUERY" | jq -sRr @uri)

# Build item types based on search type
case "$TYPE" in
  movie) ITEM_TYPES="Movie" ;;
  tv) ITEM_TYPES="Series" ;;
  all|*) ITEM_TYPES="Movie,Series" ;;
esac

# Search Jellyfin
RESULT=$(curl -s -m 10 -H "X-Emby-Token: $JELLYFIN_KEY" \
  "$JELLYFIN_URL/Items?searchTerm=$ENCODED&IncludeItemTypes=$ITEM_TYPES&Recursive=true&Fields=Path,MediaSources,PremiereDate&Limit=10" 2>/dev/null)

if [ -z "$RESULT" ]; then
  echo '{"status":"ERROR","message":"Could not connect to Jellyfin"}'
  exit 1
fi

TOTAL=$(echo "$RESULT" | jq '.TotalRecordCount // 0')

if [ "$TOTAL" = "0" ]; then
  echo '{"status":"NOT_FOUND","query":"'"$QUERY"'","type":"'"$TYPE"'","results":[]}'
  exit 0
fi

# Process results
ITEMS=$(echo "$RESULT" | jq --arg pub "$JELLYFIN_PUBLIC" '[.Items[] | {
  type: .Type,
  title: .Name,
  year: .ProductionYear,
  id: .Id,
  hasFile: ((.MediaSources // []) | length > 0),
  rating: (.OfficialRating // "NR"),
  premiered: (.PremiereDate // null),
  posterUrl: ($pub + "/Items/" + .Id + "/Images/Primary?maxWidth=300"),
  playUrl: ($pub + "/web/index.html#!/details?id=" + .Id)
}]')

# For TV series, get latest episode
ENHANCED=$(echo "$ITEMS" | jq -c '.[]' | while read -r item; do
  item_type=$(echo "$item" | jq -r '.type')
  item_id=$(echo "$item" | jq -r '.id')
  
  if [ "$item_type" = "Series" ]; then
    # Get latest episode
    LATEST=$(curl -s -m 5 -H "X-Emby-Token: $JELLYFIN_KEY" \
      "$JELLYFIN_URL/Shows/$item_id/Episodes?SortBy=PremiereDate&SortOrder=Descending&Limit=1" 2>/dev/null | \
      jq '{latestEpisode: .Items[0].Name, latestSeason: .Items[0].SeasonName, latestAired: .Items[0].PremiereDate, episodeId: .Items[0].Id}')
    echo "$item" | jq --argjson latest "$LATEST" '. + $latest'
  else
    echo "$item"
  fi
done | jq -s '.')

echo "{\"status\":\"FOUND\",\"query\":\"$QUERY\",\"type\":\"$TYPE\",\"count\":$TOTAL,\"results\":$ENHANCED}"
