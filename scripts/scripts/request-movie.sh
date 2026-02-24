#!/bin/bash
# request-movie.sh - Efficient movie request via Radarr
# Usage: ./request-movie.sh "Movie Title" [year]
# Returns JSON: {status, title, year, tmdbId, radarrId, message}

set -e

RADARR_URL="${RADARR_URL:-http://10.15.40.89:7878}"
RADARR_KEY="${RADARR_KEY:-9357c52a8209410cbfabb2cdad6480bf}"
QUALITY_PROFILE="${QUALITY_PROFILE:-4}"  # HD-1080p
ROOT_FOLDER="${ROOT_FOLDER:-/movies/}"

TITLE="$1"
YEAR="$2"

if [ -z "$TITLE" ]; then
  echo '{"status":"ERROR","message":"Usage: request-movie.sh \"Movie Title\" [year]"}'
  exit 1
fi

# Build search term
SEARCH="$TITLE"
[ -n "$YEAR" ] && SEARCH="$TITLE $YEAR"

# Search via Radarr (uses TMDB internally)
SEARCH_RESULT=$(curl -s -m 15 -H "X-Api-Key: $RADARR_KEY" \
  "$RADARR_URL/api/v3/movie/lookup?term=$(echo "$SEARCH" | jq -sRr @uri)")

if [ -z "$SEARCH_RESULT" ] || [ "$SEARCH_RESULT" = "[]" ]; then
  echo '{"status":"NOT_FOUND","message":"No results for: '"$SEARCH"'"}'
  exit 0
fi

# Get first match
MOVIE=$(echo "$SEARCH_RESULT" | jq '.[0]')
MOVIE_TITLE=$(echo "$MOVIE" | jq -r '.title')
MOVIE_YEAR=$(echo "$MOVIE" | jq -r '.year')
TMDB_ID=$(echo "$MOVIE" | jq -r '.tmdbId')

# Check if already in library
EXISTING=$(curl -s -m 10 -H "X-Api-Key: $RADARR_KEY" \
  "$RADARR_URL/api/v3/movie?tmdbId=$TMDB_ID")

if [ "$EXISTING" != "[]" ] && [ -n "$EXISTING" ]; then
  RADARR_ID=$(echo "$EXISTING" | jq -r '.[0].id')
  HAS_FILE=$(echo "$EXISTING" | jq -r '.[0].hasFile')
  if [ "$HAS_FILE" = "true" ]; then
    echo '{"status":"EXISTS","title":"'"$MOVIE_TITLE"'","year":'"$MOVIE_YEAR"',"tmdbId":'"$TMDB_ID"',"radarrId":'"$RADARR_ID"',"message":"Already in library and downloaded"}'
  else
    echo '{"status":"MONITORED","title":"'"$MOVIE_TITLE"'","year":'"$MOVIE_YEAR"',"tmdbId":'"$TMDB_ID"',"radarrId":'"$RADARR_ID"',"message":"Already monitored, waiting for download"}'
  fi
  exit 0
fi

# Prepare movie for adding
ADD_PAYLOAD=$(echo "$MOVIE" | jq '{
  title: .title,
  tmdbId: .tmdbId,
  year: .year,
  qualityProfileId: '"$QUALITY_PROFILE"',
  rootFolderPath: "'"$ROOT_FOLDER"'",
  monitored: true,
  addOptions: {
    searchForMovie: true
  }
}')

# Add to Radarr
ADD_RESULT=$(curl -s -m 15 -X POST -H "X-Api-Key: $RADARR_KEY" \
  -H "Content-Type: application/json" \
  -d "$ADD_PAYLOAD" \
  "$RADARR_URL/api/v3/movie")

# Check for errors
if echo "$ADD_RESULT" | jq -e '.id' > /dev/null 2>&1; then
  RADARR_ID=$(echo "$ADD_RESULT" | jq -r '.id')
  echo '{"status":"ADDED","title":"'"$MOVIE_TITLE"'","year":'"$MOVIE_YEAR"',"tmdbId":'"$TMDB_ID"',"radarrId":'"$RADARR_ID"',"message":"Added to Radarr, search triggered"}'
else
  ERROR=$(echo "$ADD_RESULT" | jq -r '.message // .errorMessage // "Unknown error"')
  echo '{"status":"ERROR","title":"'"$MOVIE_TITLE"'","message":"'"$ERROR"'"}'
  exit 1
fi
