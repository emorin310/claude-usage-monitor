#!/usr/bin/env python3
"""
Analyze file inventory for duplicates and patterns
"""

import os
import sys
from collections import defaultdict
from datetime import datetime

def parse_inventory_line(line):
    """Parse a line from the inventory file"""
    parts = line.strip().split('|')
    if len(parts) != 4:
        return None
    
    path, size, mtime, ftype = parts
    return {
        'path': path,
        'size': int(size),
        'mtime': mtime,
        'type': ftype,
        'basename': os.path.basename(path),
        'dirname': os.path.dirname(path),
        'ext': os.path.splitext(path)[1].lower()
    }

def analyze_inventory(inventory_file):
    """Analyze the inventory for patterns"""
    
    files = []
    size_groups = defaultdict(list)
    ext_counts = defaultdict(int)
    ext_sizes = defaultdict(int)
    large_files = []
    
    print("Reading inventory...")
    with open(inventory_file, 'r') as f:
        for line in f:
            file_info = parse_inventory_line(line)
            if file_info:
                files.append(file_info)
                
                # Group by size for duplicate detection
                size_groups[file_info['size']].append(file_info)
                
                # Count by extension
                ext_counts[file_info['ext']] += 1
                ext_sizes[file_info['ext']] += file_info['size']
                
                # Track large files (>100MB)
                if file_info['size'] > 100 * 1024 * 1024:
                    large_files.append(file_info)
    
    print(f"\nTotal files analyzed: {len(files)}")
    
    # Find potential duplicates (same size)
    print("\n=== POTENTIAL DUPLICATES (Same Size) ===")
    duplicate_candidates = {size: paths for size, paths in size_groups.items() 
                           if len(paths) > 1 and size > 1024}  # Skip tiny files
    
    wasted_space = 0
    dup_count = 0
    
    for size, paths in sorted(duplicate_candidates.items(), key=lambda x: x[0] * len(x[1]), reverse=True)[:20]:
        if len(paths) > 1:
            wasted = size * (len(paths) - 1)
            wasted_space += wasted
            dup_count += len(paths) - 1
            print(f"\n{len(paths)} files @ {size:,} bytes each (waste: {wasted:,} bytes)")
            for p in paths[:5]:  # Show first 5
                print(f"  - {p['path']}")
            if len(paths) > 5:
                print(f"  ... and {len(paths)-5} more")
    
    print(f"\nPotential wasted space from size-matched files: {wasted_space:,} bytes ({wasted_space/1024/1024:.1f} MB)")
    print(f"Potential duplicate files: {dup_count}")
    
    # Extension analysis
    print("\n=== TOP FILE TYPES ===")
    for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        size_mb = ext_sizes[ext] / 1024 / 1024
        print(f"{ext or '(no extension)':<15} {count:>6} files  {size_mb:>10.1f} MB")
    
    # Large files
    print("\n=== LARGEST FILES (>100MB) ===")
    for f in sorted(large_files, key=lambda x: x['size'], reverse=True)[:20]:
        size_gb = f['size'] / 1024 / 1024 / 1024
        print(f"{size_gb:>6.2f} GB  {f['basename']}")
        print(f"         {f['dirname']}")
    
    return files, duplicate_candidates

if __name__ == '__main__':
    inventory_file = os.path.expanduser('~/clawd-magi/bigstore-audit/file_inventory_raw.txt')
    if not os.path.exists(inventory_file):
        print(f"Inventory file not found: {inventory_file}")
        sys.exit(1)
    
    analyze_inventory(inventory_file)
