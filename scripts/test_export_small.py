#!/usr/bin/env python3
import applescript
import json

script = '''
tell application "Contacts"
    set allPeople to every person
    set output to {}
    set limit to 3
    repeat with i from 1 to limit
        set p to item i of allPeople
        set firstName to first name of p
        set lastName to last name of p
        set fullName to ""
        if firstName is not missing value then
            set fullName to firstName
        end if
        if lastName is not missing value then
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
        
        set lineStr to fullName & "|" & firstName & "|" & lastName & "|" & (my join(emailList, ";")) & "|" & (my join(phoneList, ";")) & "|" & noteText & "|" & modDateStr & "|" & createDateStr
        copy lineStr to end of output
    end repeat
    return output
end tell

on join(theList, delimiter)
    set oldDelimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to delimiter
    set theString to theList as string
    set AppleScript's text item delimiters to oldDelimiters
    return theString
end join
'''

asc = applescript.AppleScript(source=script)
lines = asc.run()
print(f"Got {len(lines)} contacts")
for line in lines:
    print(line)
    parts = line.split("|")
    print(f"Parts: {len(parts)}")
    if len(parts) >= 8:
        print(f"Mod date: {parts[6]}")
        print(f"Create date: {parts[7]}")