#!/usr/bin/env python3
"""
Export all macOS Contacts to JSON using AppleScript.
Uses pipe (|) as field separator and semicolon (;) as multi-value separator.
"""
import applescript
import json
import sys
import os
from datetime import datetime

def create_applescript() -> str:
    """Return AppleScript source that exports all contacts."""
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
        
        -- replace separators in fields
        set fullName to my replace(fullName, "|", "_")
        set firstName to my replace(firstName, "|", "_")
        set lastName to my replace(lastName, "|", "_")
        set noteText to my replace(noteText, "|", "_")
        set noteText to my replace(noteText, ";", ",")
        
        -- join multi-value lists with semicolon
        set emailStr to my join(emailList, ";")
        set phoneStr to my join(phoneList, ";")
        
        -- build line
        set lineStr to fullName & "|" & firstName & "|" & lastName & "|" & emailStr & "|" & phoneStr & "|" & noteText
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
    if len(parts) != 6:
        # fallback: try tab
        parts = line.split('\t')
    full_name, first_name, last_name, email_str, phone_str, note = parts
    emails = email_str.split(';') if email_str else []
    phones = phone_str.split(';') if phone_str else []
    return {
        'fullName': full_name,
        'firstName': first_name,
        'lastName': last_name,
        'emails': emails,
        'phones': phones,
        'note': note
    }

def export_contacts(output_path: str) -> int:
    """Export all contacts to JSON file. Returns count."""
    script_source = create_applescript()
    print("Compiling AppleScript...")
    asc = applescript.AppleScript(source=script_source)
    print("Running export (this may take a while)...")
    lines = asc.run()
    print(f"Received {len(lines)} contacts")
    
    contacts = []
    for i, line in enumerate(lines):
        try:
            contacts.append(parse_contact_line(line))
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
        'file': output_path
    }
    summary_path = os.path.join(output_dir, 'export-summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written to {summary_path}")

if __name__ == '__main__':
    main()