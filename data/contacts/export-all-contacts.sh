#!/bin/bash
# Export all iCloud contacts with pagination

OUTPUT_FILE="$HOME/clawd/data/contacts/icloud-full-export.tsv"
TEMP_DIR="$HOME/clawd/data/contacts/temp"
mkdir -p "$TEMP_DIR"

# Clean up any previous temp files
rm -f "$TEMP_DIR"/page_*.tsv

# First page (no token)
echo "Fetching page 1..."
gog contacts list --max=2000 --plain > "$TEMP_DIR/page_1.tsv"

# Check if there's a next page token in the last line
page_num=1
while true; do
    # Get the last line which might contain the page token
    last_line=$(tail -n 1 "$TEMP_DIR/page_${page_num}.tsv")
    
    # Check if it looks like a page token (base64-like string)
    if [[ "$last_line" =~ ^[A-Za-z0-9+/=_-]+$ ]] && [ ${#last_line} -gt 20 ]; then
        page_token="$last_line"
        # Remove the token line from the current file
        head -n -1 "$TEMP_DIR/page_${page_num}.tsv" > "$TEMP_DIR/page_${page_num}.tmp"
        mv "$TEMP_DIR/page_${page_num}.tmp" "$TEMP_DIR/page_${page_num}.tsv"
        
        # Fetch next page
        page_num=$((page_num + 1))
        echo "Fetching page $page_num..."
        gog contacts list --max=2000 --page="$page_token" --plain > "$TEMP_DIR/page_${page_num}.tsv"
    else
        break
    fi
done

echo "Combining all pages..."
# Combine all pages, keeping only the first header
head -n 1 "$TEMP_DIR/page_1.tsv" > "$OUTPUT_FILE"
for file in "$TEMP_DIR"/page_*.tsv; do
    tail -n +2 "$file" >> "$OUTPUT_FILE"
done

# Count results
total_count=$(tail -n +2 "$OUTPUT_FILE" | wc -l | tr -d ' ')
echo "Export complete: $total_count contacts saved to $OUTPUT_FILE"

# Clean up
rm -rf "$TEMP_DIR"
