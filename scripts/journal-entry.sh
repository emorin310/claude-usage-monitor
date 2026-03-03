#!/bin/bash
# Add a journal entry
# Usage: ./journal-entry.sh "Type" "Title" "What" "Details" "Link"

JOURNAL="$HOME/clawd/journal.md"
TODAY=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
DAY_NAME=$(date +%A)

TYPE="${1:-Activity}"
TITLE="${2:-Untitled}"
WHAT="${3:-No description}"
DETAILS="${4:-}"
LINK="${5:-}"

# Check if today's section exists, if not create it
if ! grep -q "## $TODAY" "$JOURNAL"; then
    # Insert new day section after the first ---
    sed -i '' "s/^---$/---\n\n## $TODAY ($DAY_NAME)\n/" "$JOURNAL"
fi

# Build entry
ENTRY="### $TIME - $TITLE\n- **Type:** $TYPE\n- **What:** $WHAT"
[ -n "$DETAILS" ] && ENTRY="$ENTRY\n- **Details:** $DETAILS"
[ -n "$LINK" ] && ENTRY="$ENTRY\n- **Link:** $LINK"
ENTRY="$ENTRY\n"

# Insert entry after today's date header
sed -i '' "/## $TODAY/a\\
$ENTRY
" "$JOURNAL"

# Update last modified timestamp
sed -i '' "s/\*Last updated:.*/\*Last updated: $TODAY $TIME EST\*/" "$JOURNAL"

echo "✅ Journal entry added: $TITLE"
