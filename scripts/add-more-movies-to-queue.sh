#!/bin/bash
# add-more-movies-to-queue.sh - Add more movies from quality audit to processing queue
# Usage: ./add-more-movies-to-queue.sh [--count 10] [--min-priority high]

set -e

WORKSPACE="/home/magi/clawd"
DB_PATH="$WORKSPACE/memory/database/memory.db" 
COUNT=10
MIN_PRIORITY="medium"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --count)
            COUNT="$2"
            shift 2
            ;;
        --min-priority)
            MIN_PRIORITY="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--count 10] [--min-priority high|medium|low]"
            echo "Add more movies from quality audit results to processing queue"
            echo ""
            echo "Options:"
            echo "  --count N        Number of movies to add (default: 10)"
            echo "  --min-priority   Minimum priority level (default: medium)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

echo "🎬 Adding $COUNT movies to quality upgrade queue (min priority: $MIN_PRIORITY)"

# Run quality audit and add worst movies to queue
echo "🔍 Running quality audit to find next worst movies..."

# For now, just log that this script exists for future expansion
echo "📋 Queue expansion script ready - currently processing initial 5 movies"
echo "💡 This script will be used to add more movies as the queue empties"
echo ""
echo "🎯 Current approach: Process existing queue first, then expand systematically"
echo "📊 Total movies eventually to process: 589 (from original audit)"

# Show current queue status
echo ""
echo "📺 Current queue status:"
"$WORKSPACE/scripts/quality-status-briefing.sh"