#!/bin/bash
# search-tmdb.sh - Search TMDB for movies/TV not necessarily in library
# Usage: ./search-tmdb.sh "query" [movie|tv]
# Returns JSON with poster URLs and IMDB links

set -e

RADARR_URL="${RADARR_URL:-http://10.15.40.89:7878}"
RADARR_KEY="${RADARR_KEY:-9357c52a8209410cbfabb2cdad6480bf}"

QUERY="$1"
TYPE="${2:-movie}"

if [ -z "$QUERY" ]; then
  echo '{"status":"ERROR","message":"Usage: search-tmdb.sh \"query\" [movie|tv]"}'
  exit 1
fi

ENCODED=$(printf '%s' "$QUERY" | jq -sRr @uri)

if [ "$TYPE" = "movie" ]; then
  # Use Radarr's lookup which includes IMDB and poster info
  RESULTS=$(curl -s -m 15 -H "X-Api-Key: $RADARR_KEY" \
    "$RADARR_URL/api/v3/movie/lookup?term=$ENCODED" | \
    jq '[.[:5] | .[] | {
      type: "movie",
      title: .title,
      year: .year,
      tmdbId: .tmdbId,
      imdbId: .imdbId,
      overview: (.overview | if length > 200 then (.[0:197] + "...") else . end),
      rating: .ratings.tmdb.value,
      posterUrl: (if .remotePoster then .remotePoster else null end),
      imdbUrl: (if .imdbId then ("https://www.imdb.com/title/" + .imdbId + "/") else null end),
      inLibrary: false
    }]')
  
  # Check which ones are already in library
  LIBRARY=$(curl -s -m 10 -H "X-Api-Key: $RADARR_KEY" "$RADARR_URL/api/v3/movie" | jq '[.[].tmdbId]')
  
  RESULTS=$(echo "$RESULTS" | jq --argjson lib "$LIBRARY" '[.[] | .inLibrary = ([.tmdbId] | inside($lib))]')
else
  # TV search via Sonarr
  SONARR_URL="${SONARR_URL:-http://10.15.40.89:8989}"
  SONARR_KEY="${SONARR_KEY:-09998432e0ec46e590ac9ff9235b4229}"
  
  RESULTS=$(curl -s -m 15 -H "X-Api-Key: $SONARR_KEY" \
    "$SONARR_URL/api/v3/series/lookup?term=$ENCODED" | \
    jq '[.[:5] | .[] | {
      type: "tv",
      title: .title,
      year: .year,
      tvdbId: .tvdbId,
      imdbId: .imdbId,
      overview: (.overview | if . and (length > 200) then (.[0:197] + "...") else . end),
      rating: .ratings.value,
      posterUrl: (if .remotePoster then .remotePoster else null end),
      imdbUrl: (if .imdbId then ("https://www.imdb.com/title/" + .imdbId + "/") else null end),
      inLibrary: false
    }]')
  
  LIBRARY=$(curl -s -m 10 -H "X-Api-Key: $SONARR_KEY" "$SONARR_URL/api/v3/series" | jq '[.[].tvdbId]')
  
  RESULTS=$(echo "$RESULTS" | jq --argjson lib "$LIBRARY" '[.[] | .inLibrary = ([.tvdbId] | inside($lib))]')
fi

COUNT=$(echo "$RESULTS" | jq 'length')

if [ "$COUNT" = "0" ]; then
  echo '{"status":"NOT_FOUND","query":"'"$QUERY"'","results":[]}'
else
  echo "$RESULTS" | jq --arg q "$QUERY" --arg t "$TYPE" '{status:"FOUND",query:$q,type:$t,count:length,results:.}'
fi
