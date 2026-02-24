#!/usr/bin/env python3
"""
Lean export script without progress logging.
"""
import applescript
import json
import os
from datetime import datetime

def create_applescript() -> str:
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
    repeat with p in allPeople
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
        
        -- clean separators
        set fullName to my replace(fullName, "|", "_")
        set firstName to my replace(firstName, "|", "_")
        set lastName to my replace(lastName, "|", "_")
        set noteText to my replace(noteText, "|", "_")
        set noteText to my replace(noteText, ";", ",")
        set modDateStr to my replace(modDateStr, "|", "_")
        set createDateStr to my replace(createDateStr, "|", "_")
        
        -- build line
        set lineStr to fullName & "|" & firstName & "|" & lastName & "|" & (my join(emailList, ";")) & "|" & (my join(phoneList, ";")) & "|" & noteText & "|" & modDateStr & "|" & createDateStr
        copy lineStr to end of output
    end repeat
    return output
end tell
'''

def parse_line(line: str):
    parts = line.split('|')
    if len(parts) != 8:
        return None
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

def main():
    output_dir = os.path.expanduser('~/clawd-magi/data/contacts')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'contacts-export.json')
    
    print(f"Starting export at {datetime.now()}")
    print("Compiling AppleScript...")
    asc = applescript.AppleScript(source=create_applescript())
    print("Running export...")
    lines = asc.run()
    print(f"Received {len(lines)} lines")
    
    contacts = []
    for i, line in enumerate(lines):
        if i % 1000 == 0:
            print(f"Processing {i}...")
        contact = parse_line(line)
        if contact:
            contacts.append(contact)
    
    print(f"Parsed {len(contacts)} contacts")
    
    with open(output_path, 'w') as f:
        json.dump(contacts, f, indent=2)
    
    summary = {
        'exportDate': datetime.now().isoformat(),
        'totalContacts': len(contacts),
        'file': output_path
    }
    summary_path = os.path.join(output_dir, 'export-summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Export complete. Saved to {output_path}")
    print(f"Summary: {summary_path}")

if __name__ == '__main__':
    main()