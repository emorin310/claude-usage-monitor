-- New Text File Creator
-- Creates a new blank text file in the current Finder window
-- Handles auto-incrementing: new.txt, new 2.txt, new 3.txt, etc.

on run
	tell application "Finder"
		-- Get the target folder (works even with no selection)
		try
			set targetFolder to (target of front window) as alias
		on error
			-- Fallback to Desktop if no Finder window is open
			set targetFolder to path to desktop folder
		end try
		
		set baseName to "new"
		set fileExtension to ".txt"
		set finalName to baseName & fileExtension
		set counter to 2
		
		-- Check if file exists and auto-increment
		tell application "System Events"
			set folderPath to POSIX path of targetFolder
			repeat while (exists file (folderPath & finalName))
				set finalName to baseName & " " & counter & fileExtension
				set counter to counter + 1
			end repeat
		end tell
		
		-- Create the file using touch (more reliable than Finder's make new file)
		set fullPath to POSIX path of targetFolder & finalName
		do shell script "touch " & quoted form of fullPath
		
		-- Select and reveal the new file
		set newFile to (POSIX file fullPath) as alias
		select newFile
		
		-- Optional: Open in default text editor
		-- open newFile
		
		return fullPath
	end tell
end run
