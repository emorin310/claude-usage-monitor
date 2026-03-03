#!/bin/bash
# quality-audit.sh - Scan library for low-quality movies that need replacement
# Usage: ./quality-audit.sh [--threshold 720] [--size-min 1.0] [--limit 50]
# Returns JSON with flagged movies for replacement

set -e

# Default quality thresholds
MIN_HEIGHT=720        # Minimum vertical resolution (720p)
MIN_SIZE_GB=1.0      # Minimum file size in GB
MAX_SIZE_GB=25.0     # Maximum reasonable size in GB
LIMIT=50             # Limit results for readability

# Parse command line options
while [[ $# -gt 0 ]]; do
  case $1 in
    --threshold)
      MIN_HEIGHT="$2"
      shift 2
      ;;
    --size-min)
      MIN_SIZE_GB="$2"
      shift 2
      ;;
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [--threshold 720] [--size-min 1.0] [--limit 50]"
      echo "Scan library for low-quality movies flagged for replacement"
      echo ""
      echo "Options:"
      echo "  --threshold N    Minimum vertical resolution (default: 720)"
      echo "  --size-min N     Minimum file size in GB (default: 1.0)"
      echo "  --limit N        Limit results (default: 50)"
      echo ""
      echo "Quality flags:"
      echo "  📺 LOW_RES       Below ${MIN_HEIGHT}p resolution"  
      echo "  💾 TINY_FILE     Under ${MIN_SIZE_GB}GB file size"
      echo "  📼 ANCIENT       480p or below"
      echo "  🎯 HIGH          High priority for replacement"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

RADARR_URL="${RADARR_URL:-http://10.15.40.89:7878}"
RADARR_KEY="${RADARR_KEY:-9357c52a8209410cbfabb2cdad6480bf}"

echo "🔍 Scanning library for quality issues..." >&2
echo "📏 Min resolution: ${MIN_HEIGHT}p" >&2
echo "💾 Min file size: ${MIN_SIZE_GB}GB" >&2
echo "🔢 Limit results: $LIMIT" >&2
echo "" >&2

# Get all movies with file details
echo "📡 Fetching movie data from Radarr..." >&2
MOVIES=$(curl -s -m 30 -H "X-Api-Key: $RADARR_KEY" "$RADARR_URL/api/v3/movie")

# Save to temp file to avoid command line length limits
TEMP_FILE=$(mktemp)
echo "$MOVIES" > "$TEMP_FILE"

# Count total movies with files
TOTAL_WITH_FILES=$(jq '[.[] | select(.hasFile == true)] | length' "$TEMP_FILE")
echo "📊 Found $TOTAL_WITH_FILES movies with files" >&2

# Process movies and identify quality issues
echo "🔍 Analyzing quality..." >&2

jq --argjson min_height "$MIN_HEIGHT" \
   --argjson min_size_gb "$MIN_SIZE_GB" \
   --argjson max_size_gb "$MAX_SIZE_GB" \
   --argjson limit "$LIMIT" '
{
  scanned: [.[] | select(.hasFile == true)] | length,
  thresholds: {
    min_height: $min_height,
    min_size_gb: $min_size_gb,  
    max_size_gb: $max_size_gb
  },
  flagged: ([
    .[] | 
    select(.hasFile == true) |
    . as $movie |
    {
      title: .title,
      year: .year,
      resolution: (.movieFile.mediaInfo.resolution // "unknown"),
      quality_name: (.movieFile.quality.quality.name // "unknown"),
      radarr_quality: (.movieFile.quality.quality.resolution // 0),
      sizeGB: ((.movieFile.size // 0) / 1073741824 | . * 100 | floor / 100),
      # Extract height from resolution string (e.g. "640x368" -> 368)
      height: (
        if .movieFile.mediaInfo.resolution then
          (.movieFile.mediaInfo.resolution | split("x")[1] | tonumber)
        elif .movieFile.quality.quality.resolution then
          .movieFile.quality.quality.resolution
        else 0 end
      ),
      codec: (.movieFile.mediaInfo.videoCodec // "unknown"),
      container: (.movieFile.relativePath | split(".") | .[-1] | ascii_upcase)
    } |
    . + {
      issues: [
        (if .height < $min_height then "📺 LOW_RES (\(.height)p)" else empty end),
        (if .sizeGB < $min_size_gb then "💾 TINY_FILE (\(.sizeGB)GB)" else empty end),
        (if .sizeGB > $max_size_gb then "🐋 HUGE_FILE (\(.sizeGB)GB)" else empty end),
        (if .height <= 480 then "📼 ANCIENT (\(.height)p)" else empty end),
        (if .codec == "XviD" then "🗂️ OLD_CODEC (XviD)" else empty end),
        (if .container == "AVI" then "📼 OLD_FORMAT (AVI)" else empty end)
      ],
      priority: (
        if .height <= 480 then "🎯 HIGH"
        elif .height < $min_height then "⚠️ MEDIUM"  
        elif .sizeGB < $min_size_gb then "⚠️ MEDIUM"
        elif (.codec == "XviD" or .container == "AVI") then "🔍 LOW"
        else "✅ OK"
        end
      )
    } |
    select(.issues | length > 0)
  ] | sort_by(.priority) | reverse | .[0:$limit]),
  summary: {
    total_flagged: ([.[] | select(.hasFile == true) | 
      . as $m | 
      (if $m.movieFile.mediaInfo.resolution then ($m.movieFile.mediaInfo.resolution | split("x")[1] | tonumber) elif $m.movieFile.quality.quality.resolution then $m.movieFile.quality.quality.resolution else 0 end) as $h |
      select(
        $h < $min_height or
        (($m.movieFile.size // 0) / 1073741824) < $min_size_gb or
        (($m.movieFile.size // 0) / 1073741824) > $max_size_gb or
        $h <= 480
      )
    ] | length),
    high_priority: ([.[] | select(.hasFile == true) |
      . as $m | 
      (if $m.movieFile.mediaInfo.resolution then ($m.movieFile.mediaInfo.resolution | split("x")[1] | tonumber) elif $m.movieFile.quality.quality.resolution then $m.movieFile.quality.quality.resolution else 0 end) as $h |
      select($h <= 480)
    ] | length),
    showing: $limit
  }
}' "$TEMP_FILE"

# Clean up
rm "$TEMP_FILE"