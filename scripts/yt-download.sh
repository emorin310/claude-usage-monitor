#!/usr/bin/env bash
# yt-download.sh - Download video/audio via yt-dlp
# Usage: ./yt-download.sh <url> [--audio-only] [--quality 720]
# Downloads to ~/Downloads by default

URL="${1:-}"
OUTDIR="${YTDL_OUTDIR:-$HOME/Downloads}"
AUDIO_ONLY=false
QUALITY="1080"

if [ -z "$URL" ]; then
  echo "Usage: $0 <url> [--audio-only] [--quality 720|1080|best]"
  exit 1
fi

shift
while [[ $# -gt 0 ]]; do
  case "$1" in
    --audio-only) AUDIO_ONLY=true ;;
    --quality) QUALITY="$2"; shift ;;
  esac
  shift
done

mkdir -p "$OUTDIR"

if $AUDIO_ONLY; then
  echo "🎵 Downloading audio only..."
  yt-dlp \
    --extract-audio \
    --audio-format mp3 \
    --audio-quality 0 \
    -o "$OUTDIR/%(title)s.%(ext)s" \
    "$URL"
else
  echo "🎬 Downloading video (${QUALITY}p or best available)..."
  yt-dlp \
    -f "bestvideo[height<=${QUALITY}]+bestaudio/best[height<=${QUALITY}]" \
    --merge-output-format mp4 \
    -o "$OUTDIR/%(title)s.%(ext)s" \
    "$URL"
fi

echo "✅ Done. Files saved to $OUTDIR"
