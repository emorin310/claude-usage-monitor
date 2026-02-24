#!/bin/bash
# Check Claude Usage Tool and return JSON with usage percentages

RAW=$(osascript -e '
tell application "System Events"
    tell process "Claude Usage Tool"
        click menu bar item 1 of menu bar 2
        repeat with i from 1 to 10
            delay 0.5
            if exists window 1 then exit repeat
        end repeat
        if not (exists window 1) then error "window not found"
        set w to window 1
        set allText to ""
        repeat with elem in (every static text of group 1 of group 1 of UI element "Claude Usage Tool" of group 1 of group 1 of group 1 of group 1 of w)
            set allText to allText & (value of elem as text) & "|"
        end repeat
        click menu bar item 1 of menu bar 2 -- close dropdown
        return allText
    end tell
end tell
')

# Parse and output JSON
echo "$RAW" | tr -d '\r' | awk -F'|' '{
    for(i=1; i<=NF; i++) {
        gsub(/^[ \t]+|[ \t]+$/, "", $i)
        if ($i == "All models") allmodels = $(i+1)+0
        if ($i == "Sonnet only") sonnet = $(i+1)+0
        if ($i == "Current session") session = $(i+1)+0
        if ($i == "Extra usage") extra = $(i+1)+0
    }
    printf "{\"all_models\": %d, \"sonnet_only\": %d, \"current_session\": %d, \"extra_usage\": %d}\n", allmodels, sonnet, session, extra
}'
