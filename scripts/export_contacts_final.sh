#!/bin/bash
# Export all contacts using AppleScript via osascript

set -e

OUTPUT_DIR="$HOME/clawd-magi/data/contacts"
mkdir -p "$OUTPUT_DIR"
OUTPUT_TSV="$OUTPUT_DIR/contacts-export.tsv"
OUTPUT_JSON="$OUTPUT_DIR/contacts-export.json"

# Create AppleScript
cat > /tmp/export_contacts.applescript << 'EOF'
on join(theList, delimiter)
    set oldDelimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to delimiter
    set theString to theList as string
    set AppleScript's text item delimiters to oldDelimiters
    return theString
end join

on replace(theText, search, replace)
    set oldDelimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to search
    set theItems to every text item of theText
    set AppleScript's text item delimiters to replace
    set theText to theItems as string
    set AppleScript's text item delimiters to oldDelimiters
    return theText
end replace

tell application "Contacts"
    set allPeople to every person
    set total to count of allPeople
    
    repeat with i from 1 to total
        set p to item i of allPeople
        
        -- first name
        set firstName to first name of p
        if firstName is missing value then
            set firstName to ""
        end if
        
        -- last name
        set lastName to last name of p
        if lastName is missing value then
            set lastName to ""
        end if
        
        -- full name
        set fullName to ""
        if firstName is not "" then
            set fullName to firstName
        end if
        if lastName is not "" then
            if fullName is not "" then
                set fullName to fullName & " " & lastName
            else
                set fullName to lastName
            end if
        end if
        
        -- emails
        set emailList to {}
        repeat with e in emails of p
            set emailValue to value of e
            copy emailValue as text to end of emailList
        end repeat
        
        -- phones
        set phoneList to {}
        repeat with ph in phones of p
            set phoneValue to value of ph
            copy phoneValue as text to end of phoneList
        end repeat
        
        -- notes
        set noteText to note of p
        if noteText is missing value then
            set noteText to ""
        end if
        
        -- modification date
        set modDate to modification date of p
        if modDate is missing value then
            set modDateStr to ""
        else
            set modDateStr to modDate as text
        end if
        
        -- creation date
        set createDate to creation date of p
        if createDate is missing value then
            set createDateStr to ""
        else
            set createDateStr to createDate as text
        end if
        
        -- Clean separators and newlines
        set fullName to my replace(fullName, "	", " ")
        set firstName to my replace(firstName, "	", " ")
        set lastName to my replace(lastName, "	", " ")
        set noteText to my replace(noteText, "	", " ")
        set noteText to my replace(noteText, "
", " | ")
        set modDateStr to my replace(modDateStr, "	", " ")
        set createDateStr to my replace(createDateStr, "	", " ")
        
        -- Join lists
        set emailStr to my join(emailList, ";")
        set phoneStr to my join(phoneList, ";")
        
        -- Output tab-separated line
        set lineStr to fullName & "	" & firstName & "	" & lastName & "	" & emailStr & "	" & phoneStr & "	" & noteText & "	" & modDateStr & "	" & createDateStr
        log lineStr
        
        -- Progress every 500 contacts
        if i mod 500 is 0 then
            log "Progress: " & i & " of " & total
        end if
    end repeat
end tell
EOF

echo "Exporting contacts to $OUTPUT_TSV..."
echo -e "FullName\tFirstName\tLastName\tEmails\tPhones\tNote\tModificationDate\tCreationDate" > "$OUTPUT_TSV"

# Run AppleScript, capture log output (goes to stderr), filter out progress messages
osascript /tmp/export_contacts.applescript 2>&1 | grep -v "^Progress:" >> "$OUTPUT_TSV"

echo "Export complete. Converting to JSON..."

# Convert TSV to JSON using Python
python3 << EOF
import json
import csv
import sys

tsv_file = "$OUTPUT_TSV"
json_file = "$OUTPUT_JSON"

contacts = []
with open(tsv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        # Parse semicolon-separated lists
        emails = row['Emails'].split(';') if row['Emails'] else []
        phones = row['Phones'].split(';') if row['Phones'] else []
        
        contacts.append({
            'fullName': row['FullName'],
            'firstName': row['FirstName'],
            'lastName': row['LastName'],
            'emails': emails,
            'phones': phones,
            'note': row['Note'],
            'modificationDate': row['ModificationDate'],
            'creationDate': row['CreationDate']
        })

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(contacts, f, indent=2, ensure_ascii=False)

print(f"Converted {len(contacts)} contacts to JSON")
EOF

echo "Done. Files created:"
echo "  - $OUTPUT_TSV"
echo "  - $OUTPUT_JSON"