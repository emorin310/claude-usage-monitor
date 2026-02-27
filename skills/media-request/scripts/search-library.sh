#!/bin/bash
# search-library.sh - Search existing movie/TV library with rich info
# Usage: ./search-library.sh "query" [movie|tv|all]
# Returns JSON with poster URLs and Jellyfin links

set -e

RADARR_URL="${RADARR_URL:-http://10.15.40.89:7878}"
RADARR_KEY="${RADARR_KEY:-9357c52a8209410cbfabb2cdad6480bf}"
SONARR_URL="${SONARR_URL:-http://10.15.40.89:8989}"
SONARR_KEY="${SONARR_KEY:-09998432e0ec46e590ac9ff9235b4229}"
JELLYFIN_URL="${JELLYFIN_URL:-http://192.168.1.96:8096}"
JELLYFIN_KEY="${JELLYFIN_KEY:-c5b4d7fc157b49778470414e5944b0b2}"
JELLYFIN_PUBLIC="${JELLYFIN_PUBLIC:-https://jellyfin.ericmorin.online}"

QUERY="$1"
TYPE="${2:-all}"

if [ -z "$QUERY" ]; then
  echo '{"status":"ERROR","message":"Usage: search-library.sh \"query\" [movie|tv|all]"}'
  exit 1
fi

PATTERN=$(echo "$QUERY" | sed 's/[^a-zA-Z0-9 ]//g')

# Function to get Jellyfin ID for a title
get_jellyfin_info() {
  local TITLE="$1"
  local YEAR="$2"
  local ITEM_TYPE="$3"  # Movie or Series
  
  ENCODED=$(printf '%s' "$TITLE" | jq -sRr @uri)
  JF_RESULT=$(curl -s -m 10 -H "X-Emby-Token: $JELLYFIN_KEY" \
    "$JELLYFIN_URL/Items?searchTerm=$ENCODED&IncludeItemTypes=$ITEM_TYPE&Recursive=true&Limit=3" 2>/dev/null)
  
  if [ -n "$YEAR" ]; then
    MATCH=$(echo "$JF_RESULT" | jq --arg y "$YEAR" '[.Items[] | select(.ProductionYear == ($y|tonumber))][0] // .Items[0] // null')
  else
    MATCH=$(echo "$JF_RESULT" | jq '.Items[0] // null')
  fi
  
  if [ "$MATCH" != "null" ] && [ -n "$MATCH" ]; then
    JF_ID=$(echo "$MATCH" | jq -r '.Id')
    echo "$JF_ID"
  else
    echo ""
  fi
}

RESULTS="[]"

# Search movies
if [ "$TYPE" = "movie" ] || [ "$TYPE" = "all" ]; then
  MOVIES=$(curl -s -m 15 -H "X-Api-Key: $RADARR_KEY" "$RADARR_URL/api/v3/movie")
  
  while read -r MOVIE; do
    [ -z "$MOVIE" ] && continue
    TITLE=$(echo "$MOVIE" | jq -r '.title')
    YEAR=$(echo "$MOVIE" | jq -r '.year')
    RADARR_ID=$(echo "$MOVIE" | jq -r '.id')
    HAS_FILE=$(echo "$MOVIE" | jq -r '.hasFile')
    TMDB_ID=$(echo "$MOVIE" | jq -r '.tmdbId')
    IMDB_ID=$(echo "$MOVIE" | jq -r '.imdbId // empty')
    QUALITY=$(echo "$MOVIE" | jq -r '.movieFile.quality.quality.name // null')
    SIZE=$(echo "$MOVIE" | jq -r 'if .movieFile.size then ((.movieFile.size / 1073741824 * 100 | floor) / 100) else null end')
    
    # Get Jellyfin info
    JF_ID=$(get_jellyfin_info "$TITLE" "$YEAR" "Movie")
    
    if [ -n "$JF_ID" ]; then
      POSTER="$JELLYFIN_PUBLIC/Items/$JF_ID/Images/Primary?maxWidth=300"
      PLAY_URL="$JELLYFIN_PUBLIC/web/index.html#/details?id=$JF_ID"
    else
      POSTER="https://image.tmdb.org/t/p/w300/$(curl -s "https://api.themoviedb.org/3/movie/$TMDB_ID?api_key=YOUR_KEY" 2>/dev/null | jq -r '.poster_path // empty')"
      PLAY_URL=""
    fi
    
    IMDB_URL=""
    [ -n "$IMDB_ID" ] && IMDB_URL="https://www.imdb.com/title/$IMDB_ID/"
    
    ITEM=$(jq -n \
      --arg type "movie" \
      --arg title "$TITLE" \
      --arg year "$YEAR" \
      --arg rid "$RADARR_ID" \
      --arg hf "$HAS_FILE" \
      --arg q "$QUALITY" \
      --arg s "$SIZE" \
      --arg jid "$JF_ID" \
      --arg poster "$POSTER" \
      --arg play "$PLAY_URL" \
      --arg imdb "$IMDB_URL" \
      '{
        type: $type,
        title: $title,
        year: ($year|tonumber),
        radarrId: ($rid|tonumber),
        hasFile: ($hf == "true"),
        quality: (if $q == "null" then null else $q end),
        sizeGB: (if $s == "null" then null else ($s|tonumber) end),
        jellyfinId: (if $jid == "" then null else $jid end),
        posterUrl: (if $poster == "" then null else $poster end),
        playUrl: (if $play == "" then null else $play end),
        imdbUrl: (if $imdb == "" then null else $imdb end)
      }')
    
    RESULTS=$(echo "$RESULTS" | jq --argjson item "$ITEM" '. + [$item]')
    
  done < <(echo "$MOVIES" | jq -c --arg q "$PATTERN" '.[] | select(.title | test($q; "i"))' | head -5)
fi

# Search TV
if [ "$TYPE" = "tv" ] || [ "$TYPE" = "all" ]; then
  SHOWS=$(curl -s -m 15 -H "X-Api-Key: $SONARR_KEY" "$SONARR_URL/api/v3/series")
  
  while read -r SHOW; do
    [ -z "$SHOW" ] && continue
    TITLE=$(echo "$SHOW" | jq -r '.title')
    YEAR=$(echo "$SHOW" | jq -r '.year')
    SONARR_ID=$(echo "$SHOW" | jq -r '.id')
    TVDB_ID=$(echo "$SHOW" | jq -r '.tvdbId // empty')
    IMDB_ID=$(echo "$SHOW" | jq -r '.imdbId // empty')
    SEASONS=$(echo "$SHOW" | jq -r '.seasonCount')
    EPISODES=$(echo "$SHOW" | jq -r '.episodeFileCount // 0')
    
    JF_ID=$(get_jellyfin_info "$TITLE" "$YEAR" "Series")
    
    if [ -n "$JF_ID" ]; then
      POSTER="$JELLYFIN_PUBLIC/Items/$JF_ID/Images/Primary?maxWidth=300"
      PLAY_URL="$JELLYFIN_PUBLIC/web/index.html#/details?id=$JF_ID"
    else
      POSTER=""
      PLAY_URL=""
    fi
    
    IMDB_URL=""
    [ -n "$IMDB_ID" ] && IMDB_URL="https://www.imdb.com/title/$IMDB_ID/"
    
    ITEM=$(jq -n \
      --arg type "tv" \
      --arg title "$TITLE" \
      --arg year "$YEAR" \
      --arg sid "$SONARR_ID" \
      --arg seasons "$SEASONS" \
      --arg eps "$EPISODES" \
      --arg jid "$JF_ID" \
      --arg poster "$POSTER" \
      --arg play "$PLAY_URL" \
      --arg imdb "$IMDB_URL" \
      '{
        type: $type,
        title: $title,
        year: (if $year == "" or $year == "null" then null else ($year|tonumber) end),
        sonarrId: (if $sid == "" or $sid == "null" then null else ($sid|tonumber) end),
        seasons: (if $seasons == "" or $seasons == "null" then 0 else ($seasons|tonumber) end),
        episodes: (if $eps == "" or $eps == "null" then 0 else ($eps|tonumber) end),
        jellyfinId: (if $jid == "" then null else $jid end),
        posterUrl: (if $poster == "" then null else $poster end),
        playUrl: (if $play == "" then null else $play end),
        imdbUrl: (if $imdb == "" then null else $imdb end)
      }')
    
    RESULTS=$(echo "$RESULTS" | jq --argjson item "$ITEM" '. + [$item]')
    
  done < <(echo "$SHOWS" | jq -c --arg q "$PATTERN" '.[] | select(.title | test($q; "i"))' | head -5)
fi

COUNT=$(echo "$RESULTS" | jq 'length')

if [ "$COUNT" = "0" ]; then
  echo '{"status":"NOT_FOUND","query":"'"$QUERY"'","results":[],"message":"No matches in library"}'
else
  echo "$RESULTS" | jq --arg q "$QUERY" '{status:"FOUND",query:$q,count:length,results:.}'
fi
