#!/bin/bash
# Setup keyboard shortcut for "New Text File" quick action
# Default: ⌃⌥⌘N (Ctrl+Option+Cmd+N)

SHORTCUT="${1:-^~@n}"  # ^ = Ctrl, ~ = Option, @ = Cmd, n = N

echo "Setting keyboard shortcut for 'New Text File' in Finder..."

# Add the shortcut to Finder's user key equivalents
defaults write com.apple.finder NSUserKeyEquivalents -dict-add "New Text File" "$SHORTCUT"

# Restart Finder to apply
killall Finder

echo "✅ Done! Keyboard shortcut set."
echo ""
echo "To use: Open a Finder window and press ⌃⌥⌘N"
echo ""
echo "To change the shortcut, edit via:"
echo "  System Settings → Keyboard → Keyboard Shortcuts → Services"
