#!/bin/bash

# Find real duplicates using MD5 hashing
# Focus on files >1MB to find significant duplicates

AUDIT_DIR=~/clawd/bigstore-audit
TARGET=/Volumes/bigstore/REVIEW

echo "Finding duplicate candidates (files >1MB, same size)..."

# First, find files by size, then hash files with duplicate sizes
find "$TARGET" -type f -size +1M -print0 2>/dev/null | \
  xargs -0 stat -f "%z|%N" 2>/dev/null | \
  sort -t'|' -k1,1n | \
  awk -F'|' '{
    size=$1; 
    path=$2; 
    sizes[size]++; 
    paths[size]=paths[size] "\n" path
  } 
  END {
    for (s in sizes) {
      if (sizes[s] > 1) {
        printf "%s|%d%s\n", s, sizes[s], paths[s]
      }
    }
  }' > "$AUDIT_DIR/duplicate_size_candidates.txt"

echo "Found $(wc -l < $AUDIT_DIR/duplicate_size_candidates.txt) size groups with potential duplicates"

# Now hash the top candidates (excluding .7z.NNN multi-volume archives)
echo "Hashing potential duplicates (this will take time)..."

cat "$AUDIT_DIR/duplicate_size_candidates.txt" | while IFS='|' read -r size count paths; do
  # Skip small groups
  if [ "$count" -lt 2 ]; then
    continue
  fi
  
  # Skip if size suggests multi-volume archive pattern
  if [ "$size" = "104857600" ] || [ "$size" = "250609664" ]; then
    echo "Skipping common archive chunk size: $size bytes"
    continue
  fi
  
  # Get file paths for this size
  echo "$paths" | while read -r filepath; do
    if [ -n "$filepath" ] && [ -f "$filepath" ]; then
      # Exclude .7z.### files (multi-volume archives)
      if [[ ! "$filepath" =~ \.7z\.[0-9]{3}/ ]]; then
        md5=$(md5 -q "$filepath" 2>/dev/null)
        if [ -n "$md5" ]; then
          echo "$md5|$size|$filepath"
        fi
      fi
    fi
  done
done > "$AUDIT_DIR/file_hashes.txt"

echo "Analyzing hashes for real duplicates..."

# Find files with same MD5
sort "$AUDIT_DIR/file_hashes.txt" | \
  awk -F'|' '{
    hash=$1;
    size=$2;
    path=$3;
    hashes[hash]++;
    hash_sizes[hash]=size;
    hash_paths[hash]=hash_paths[hash] "\n  " path
  }
  END {
    for (h in hashes) {
      if (hashes[h] > 1) {
        waste = hash_sizes[h] * (hashes[h] - 1);
        printf "\n%d duplicates @ %s bytes each (waste: %s bytes)\n%s\n", \
          hashes[h], hash_sizes[h], waste, hash_paths[h]
      }
    }
  }' > "$AUDIT_DIR/real_duplicates.txt"

echo "Done! Results in real_duplicates.txt"
wc -l "$AUDIT_DIR/real_duplicates.txt"
