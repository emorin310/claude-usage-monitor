#!/bin/bash

AUDIT_DIR=~/clawd-magi/bigstore-audit
TARGET=/Volumes/bigstore/REVIEW

echo "=== Starting Comprehensive Audit ===" > $AUDIT_DIR/audit_log.txt
echo "Start time: $(date)" >> $AUDIT_DIR/audit_log.txt

# 1. Overall size
echo "Getting overall size..." >> $AUDIT_DIR/audit_log.txt
du -sh $TARGET 2>/dev/null > $AUDIT_DIR/total_size.txt

# 2. File and directory counts
echo "Counting files and directories..." >> $AUDIT_DIR/audit_log.txt
find $TARGET -type f 2>/dev/null | wc -l | tr -d ' ' > $AUDIT_DIR/file_count.txt
find $TARGET -type d 2>/dev/null | wc -l | tr -d ' ' > $AUDIT_DIR/dir_count.txt

# 3. Top-level folder sizes
echo "Analyzing folder sizes..." >> $AUDIT_DIR/audit_log.txt
du -sh $TARGET/* 2>/dev/null | sort -rh > $AUDIT_DIR/toplevel_sizes.txt

# 4. File extensions
echo "Analyzing file types..." >> $AUDIT_DIR/audit_log.txt
find $TARGET -type f 2>/dev/null | sed 's/.*\.//' | tr '[:upper:]' '[:lower:]' | sort | uniq -c | sort -rn > $AUDIT_DIR/extensions.txt

# 5. Largest files (top 100)
echo "Finding largest files..." >> $AUDIT_DIR/audit_log.txt
find $TARGET -type f -exec ls -lh {} \; 2>/dev/null | awk '{print $5 "\t" $9}' | sort -rh | head -100 > $AUDIT_DIR/largest_files.txt

# 6. Detailed inventory with metadata
echo "Building detailed inventory..." >> $AUDIT_DIR/audit_log.txt
find $TARGET -type f -print0 2>/dev/null | xargs -0 stat -f "%N|%z|%Sm|%HT" -t "%Y-%m-%d %H:%M:%S" 2>/dev/null > $AUDIT_DIR/full_inventory.txt

# 7. Directory sizes (second level)
echo "Analyzing all subdirectories..." >> $AUDIT_DIR/audit_log.txt
find $TARGET -maxdepth 2 -type d -exec du -sh {} \; 2>/dev/null | sort -rh > $AUDIT_DIR/subdirectory_sizes.txt

echo "Audit complete: $(date)" >> $AUDIT_DIR/audit_log.txt
