#!/usr/bin/env python3
import applescript
import json

script = '''
tell application "Contacts"
    set p to first person
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
    
    set emailList to {}
    repeat with e in emails of p
        set emailValue to value of e
        copy emailValue as text to end of emailList
    end repeat
    
    set phoneList to {}
    repeat with ph in phones of p
        set phoneValue to value of ph
        copy phoneValue as text to end of phoneList
    end repeat
    
    set noteText to note of p
    if noteText is missing value then
        set noteText to ""
    end if
    
    return {fullName:fullName, firstName:firstName as text, lastName:lastName as text, emails:emailList, phones:phoneList, note:noteText as text}
end tell
'''

asc = applescript.AppleScript(source=script)
result = asc.run()
print("Result type:", type(result))
print("Result:", result)
print("JSON:", json.dumps(result, default=str))