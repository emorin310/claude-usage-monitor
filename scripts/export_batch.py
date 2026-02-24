#!/usr/bin/env python3
import applescript
import json

script = '''
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
    set output to {}
    set limit to 5
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
        
        -- replace separators
        set fullName to my replace(fullName, "|", "_")
        set firstName to my replace(firstName as text, "|", "_")
        set lastName to my replace(lastName as text, "|", "_")
        set noteText to my replace(noteText as text, "|", "_")
        
        set emailStr to my join(emailList, ";")
        set phoneStr to my join(phoneList, ";")
        
        set lineStr to fullName & "|" & firstName & "|" & lastName & "|" & emailStr & "|" & phoneStr & "|" & noteText
        copy lineStr to end of output
    end repeat
    return output
end tell
'''

asc = applescript.AppleScript(source=script)
result = asc.run()
print("Number of lines:", len(result))
for line in result:
    print(line)
    parts = line.split("|")
    print("Parts:", parts)