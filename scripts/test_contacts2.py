#!/usr/bin/env python3
import applescript
import json

script = '''
tell application "Contacts"
    set allPeople to every person
    set output to {}
    set limit to 2
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
        
        set rec to {fullName:fullName, firstName:firstName as text, lastName:lastName as text, emails:emailList, phones:phoneList, note:noteText as text}
        copy rec to end of output
    end repeat
    return output
end tell
'''

try:
    result = applescript.run(script)
    print(f"Type: {type(result)}")
    print(f"Result: {result}")
    # Try to convert to Python list
    if hasattr(result, '__iter__'):
        for r in result:
            print(r)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()