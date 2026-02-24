#!/usr/bin/env python3
"""
Export all contacts from macOS Contacts.app to JSON file.
Uses AppleScript via osascript.
"""
import json
import subprocess
import sys
import os
import tempfile

def run_applescript(script):
    """Run AppleScript and return stdout."""
    cmd = ['osascript', '-e', script]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e.stderr}", file=sys.stderr)
        raise

def get_contacts_count():
    """Return total number of contacts."""
    script = 'tell application "Contacts" to return count of every person'
    return int(run_applescript(script))

def export_contacts_to_json(output_path):
    """Export all contacts to JSON file."""
    # Write AppleScript to a temporary file to avoid command line length limits
    applescript = '''
    on joinList(theList, delimiter)
        set oldDelimiters to AppleScript's text item delimiters
        set AppleScript's text item delimiters to delimiter
        set theString to theList as string
        set AppleScript's text item delimiters to oldDelimiters
        return theString
    end joinList

    on escapeJson(theText)
        set oldDelimiters to AppleScript's text item delimiters
        set AppleScript's text item delimiters to "\\\\"
        set theItems to every text item of theText
        set AppleScript's text item delimiters to "\\\\\\\\"
        set theString to theItems as string
        set AppleScript's text item delimiters to oldDelimiters
        
        set oldDelimiters to AppleScript's text item delimiters
        set AppleScript's text item delimiters to "\\""
        set theItems to every text item of theString
        set AppleScript's text item delimiters to "\\\\\\""
        set theString to theItems as string
        set AppleScript's text item delimiters to oldDelimiters
        
        set oldDelimiters to AppleScript's text item delimiters
        set AppleScript's text item delimiters to "
"
        set theItems to every text item of theString
        set AppleScript's text item delimiters to "\\\\n"
        set theString to theItems as string
        set AppleScript's text item delimiters to oldDelimiters
        
        set oldDelimiters to AppleScript's text item delimiters
        set AppleScript's text item delimiters to "	"
        set theItems to every text item of theString
        set AppleScript's text item delimiters to "\\\\t"
        set theString to theItems as string
        set AppleScript's text item delimiters to oldDelimiters
        
        return theString
    end escapeJson

    tell application "Contacts"
        set allPeople to every person
        set output to {}
        repeat with p in allPeople
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
            repeat with email in emails of p
                set emailValue to value of email
                copy emailValue as text to end of emailList
            end repeat
            
            -- phones
            set phoneList to {}
            repeat with phone in phones of p
                set phoneValue to value of phone
                copy phoneValue as text to end of phoneList
            end repeat
            
            -- notes
            set noteText to note of p
            if noteText is missing value then
                set noteText to ""
            end if
            
            -- Build JSON manually
            set jsonStr to "{"
            set jsonStr to jsonStr & "\\"fullName\\":\\"" & escapeJson(fullName) & "\\","
            set jsonStr to jsonStr & "\\"firstName\\":\\"" & escapeJson(firstName as text) & "\\","
            set jsonStr to jsonStr & "\\"lastName\\":\\"" & escapeJson(lastName as text) & "\\","
            set jsonStr to jsonStr & "\\"emails\\":[" & joinList(emailList, ",") & "],"
            set jsonStr to jsonStr & "\\"phones\\":[" & joinList(phoneList, ",") & "],"
            set jsonStr to jsonStr & "\\"note\\":\\"" & escapeJson(noteText as text) & "\\""
            set jsonStr to jsonStr & "}"
            copy jsonStr to end of output
        end repeat
        return "[" & joinList(output, ",") & "]"
    end tell
    '''
    
    # Write to temporary .scpt file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.scpt', delete=False) as f:
        f.write(applescript)
        script_path = f.name
    
    try:
        # Run the script
        result = subprocess.run(['osascript', script_path], capture_output=True, text=True, check=True)
        json_output = result.stdout.strip()
        # Validate JSON
        data = json.loads(json_output)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exported {len(data)} contacts to {output_path}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON output: {e}", file=sys.stderr)
        print("First 500 chars of output:", json_output[:500], file=sys.stderr)
        raise
    finally:
        os.unlink(script_path)

def main():
    output_dir = os.path.expanduser('~/clawd-magi/data/contacts')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'contacts-export.json')
    
    print(f"Total contacts: {get_contacts_count()}")
    print("Exporting...")
    export_contacts_to_json(output_path)
    print("Done.")

if __name__ == '__main__':
    main()