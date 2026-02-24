#!/usr/bin/env python3
"""
Export all macOS Contacts to JSON using AppleScript, including modification dates.
"""
import applescript
import json
import sys
import os
from datetime import datetime

def create_applescript() -> str:
    """Return AppleScript source that exports all contacts with modification dates."""
    return '''
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
    set output to {}
    set batchSize to 500
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
        
        -- full name (constructed)
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
        
        -- replace separators in fields
        set fullName to my replace(fullName, "|", "_")
        set firstName to my replace(firstName, "|", "_")
        set lastName to my replace(lastName, "|", "_")
        set noteText to my replace(noteText, "|", "_")
        set noteText to my replace(noteText, ";", ",")
        set modDateStr to my replace(modDateStr, "|", "_")
        set createDateStr to my replace(createDateStr, "|", "_")
        
        -- join multi-value lists with semicolon
        set emailStr to my join(emailList, ";")
        set phoneStr to my join(phoneList, ";")
        
        -- build line: 8 fields
        set lineStr to fullName & "|" & firstName & "|" & lastName & "|" & emailStr & "|" & phoneStr & "|" & noteText & "|" & modDateStr & "|" & createDateStr
        copy lineStr to end of output
        
        -- progress log
        if i mod batchSize is 0 then
            log "Exported " & i & " of " & total
        end if
    end repeat
    log "Export complete: " & total & " contacts"
    return output
end tell
'''

def parse_contact_line(line: str) -> dict:
    """Parse a pipe-separated line into a contact dict."""
    parts = line.split('|')
    if len(parts) != 8:
        # fallback for older format or corrupted lines
        if len(parts) == 6:
            # old format without dates
            full_name, first_name, last_name, email_str, phone_str, note = parts
            mod_date = ""
            create_date = ""
        else:
            print(f"Warning: Unexpected number of parts ({len(parts)}) in line: {line[:100]}")
            return None
    else:
        full_name, first_name, last_name, email_str, phone_str, note, mod_date, create_date = parts
    
    emails = email_str.split(';') if email_str else []
    phones = phone_str.split(';') if phone_str else []
    
    return {
        'fullName': full_name,
        'firstName': first_name,
        'lastName': last_name,
        'emails': emails,
        'phones': phones,
        'note': note,
        'modificationDate': mod_date,
        'creationDate': create_date
    }

def export_contacts(output_path: str) -> int:
    """Export all contacts to JSON file. Returns count."""
    script_source = create_applescript()
    print("Compiling AppleScript...")
    asc = applescript.AppleScript(source=script_source)
    print("Running export (this may take a while for 6919 contacts)...")
    lines = asc.run()
    print(f"Received {len(lines)} contacts")
    
    contacts = []
    for i, line in enumerate(lines):
        try:
            contact = parse_contact_line(line)
            if contact:
                contacts.append(contact)
        except Exception as e:
            print(f"Error parsing line {i}: {e}")
            continue
    
    print(f"Parsed {len(contacts)} contacts")
    
    with open(output_path, 'w') as f:
        json.dump(contacts, f, indent=2)
    
    return len(contacts)

def main():
    output_dir = os.path.expanduser('~/clawd-magi/data/contacts')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'contacts-export.json')
    
    print(f"Starting export at {datetime.now()}")
    count = export_contacts(output_path)
    print(f"Exported {count} contacts to {output_path}")
    
    # Also write a summary file
    summary = {
        'exportDate': datetime.now().isoformat(),
        'totalContacts': count,
        'file': output_path,
        'includesDates': True
    }
    summary_path = os.path.join(output_dir, 'export-summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written to {summary_path}")

if __name__ == '__main__':
    main()