#!/usr/bin/env python3
"""
Quick personal document search focused on key BigStore directories.
Optimized for performance by targeting specific document folders.
"""

import os
import json
import argparse
from pathlib import Path

def search_targeted_directories(query):
    """Search specific directories for documents matching query."""
    
    # Key document directories in BigStore
    target_dirs = [
        "/mnt/bigstore/REVIEW/DOCUMENTS/Health",
        "/mnt/bigstore/REVIEW/DOCUMENTS/Tina", 
        "/mnt/bigstore/REVIEW/DOCUMENTS/scanned docs",
        "/mnt/bigstore/REVIEW/DOCUMENTS/IT",
        "/mnt/bigstore/REVIEW/DOCUMENTS/Eric",  # If it exists
        "/mnt/bigstore/REVIEW/DOCUMENTS"  # Root level
    ]
    
    results = []
    search_terms = query.lower().split()
    
    for dir_path in target_dirs:
        if not Path(dir_path).exists():
            continue
            
        print(f"Searching: {dir_path}")
        
        try:
            # Use find command for efficiency
            if dir_path.endswith("DOCUMENTS"):
                # Root level - limit depth to avoid deep scanning
                cmd = f'find "{dir_path}" -maxdepth 2 -type f \\( -name "*.pdf" -o -name "*.jpg" -o -name "*.png" \\)'
            else:
                # Subdirectories - scan deeper
                cmd = f'find "{dir_path}" -type f \\( -name "*.pdf" -o -name "*.jpg" -o -name "*.png" \\)'
            
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                
                for filepath in files:
                    if not filepath:
                        continue
                        
                    filename = os.path.basename(filepath).lower()
                    
                    # Check if any search term matches filename
                    if any(term in filename for term in search_terms):
                        # Get file info
                        try:
                            stat = os.stat(filepath)
                            results.append({
                                'name': os.path.basename(filepath),
                                'path': filepath,
                                'directory': os.path.dirname(filepath),
                                'size': stat.st_size,
                                'category': categorize_file(filepath)
                            })
                        except:
                            continue
                            
        except Exception as e:
            print(f"Error searching {dir_path}: {e}")
            continue
    
    return results

def categorize_file(filepath):
    """Simple file categorization."""
    path_lower = filepath.lower()
    name_lower = os.path.basename(filepath).lower()
    
    if '/health/' in path_lower or any(term in name_lower for term in ['medical', 'prescription', 'doctor']):
        return 'medical'
    elif any(term in name_lower for term in ['tax', 't1', 't4', 'cra']):
        return 'tax'
    elif any(term in name_lower for term in ['passport', 'sin', 'license', 'licence']):
        return 'identity'
    elif any(term in name_lower for term in ['insurance', 'policy']):
        return 'insurance'
    else:
        return 'document'

def main():
    parser = argparse.ArgumentParser(description='Quick search of BigStore documents')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--format', choices=['json', 'table'], default='table')
    
    args = parser.parse_args()
    
    results = search_targeted_directories(args.query)
    
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"No documents found matching: {args.query}")
        else:
            print(f"Found {len(results)} documents:")
            print("=" * 80)
            
            # Group by category
            by_category = {}
            for result in results:
                category = result['category']
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(result)
            
            for category, files in by_category.items():
                print(f"\n📁 {category.upper()} DOCUMENTS:")
                for file in files:
                    print(f"  • {file['name']}")
                    print(f"    📍 {file['path']}")
                    print(f"    📁 Directory: {os.path.basename(file['directory'])}")
                    print()

if __name__ == '__main__':
    main()