# New Text File - Finder Quick Action

Creates a new blank text file in the current Finder window location. Works when right-clicking on whitespace (no file selection required).

## Features
- Creates `new.txt` in the current Finder folder
- Auto-increments if file exists: `new.txt` → `new 2.txt` → `new 3.txt`
- Works from Services menu (right-click anywhere in Finder)
- Can be assigned a keyboard shortcut

## Installation

The workflow is already installed at:
```
~/Library/Services/NewTextFile.workflow
```

## Usage

1. **Right-click in Finder** (anywhere - whitespace or file)
2. Go to **Services** → **New Text File**
3. A new `new.txt` file appears, selected and ready to rename

## Adding a Keyboard Shortcut

1. Open **System Settings** → **Keyboard** → **Keyboard Shortcuts**
2. Select **Services** in the left sidebar
3. Expand **Files and Folders** (or search for "New Text File")
4. Click "none" next to **New Text File** and press your desired shortcut
   - Recommended: `⌃⌥⌘N` (Ctrl+Option+Cmd+N)

## Alternative: Assign via Terminal

```bash
# Add keyboard shortcut ⌃⌥⌘N for "New Text File" in Finder
defaults write com.apple.finder NSUserKeyEquivalents -dict-add "New Text File" "^~@n"
killall Finder
```

## Troubleshooting

**Service not appearing?**
```bash
/System/Library/CoreServices/pbs -flush
killall Finder
```

**Need to reinstall?**
```bash
rm -rf ~/Library/Services/NewTextFile.workflow
# Then run the install script or copy the workflow back
```

## Files

- `NewTextFile.applescript` - Standalone AppleScript (can be run directly)
- `~/Library/Services/NewTextFile.workflow` - Automator Quick Action bundle
