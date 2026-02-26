#!/usr/bin/env python3
"""
Data Discovery Script for Obsidian Second Brain

Scans specified paths to inventory available data sources for migration.
Identifies file types, sizes, and suggests processing strategies.
"""

import os
import json
import argparse
from pathlib import Path
from collections import defaultdict, Counter
import mimetypes
from datetime import datetime

class DataDiscoverer:
    def __init__(self):
        self.file_types = defaultdict(list)
        self.size_stats = defaultdict(int)
        self.date_range = {"earliest": None, "latest": None}
        self.total_files = 0
        self.total_size = 0
        
    def scan_path(self, path, max_depth=3):
        """Recursively scan a path for files and categorize them."""
        try:
            path = Path(path).expanduser()
            if not path.exists():
                print(f"Warning: Path {path} does not exist")
                return
                
            print(f"Scanning: {path}")
            
            for root, dirs, files in os.walk(path):
                current_depth = len(Path(root).relative_to(path).parts)
                if current_depth > max_depth:
                    dirs.clear()  # Don't descend further
                    continue
                    
                for file in files:
                    file_path = Path(root) / file
                    self._analyze_file(file_path)
                    
        except Exception as e:
            print(f"Error scanning {path}: {e}")
    
    def _analyze_file(self, file_path):
        """Analyze a single file and categorize it."""
        try:
            stat = file_path.stat()
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime)
            
            # Update stats
            self.total_files += 1
            self.total_size += size
            
            # Track date range
            if self.date_range["earliest"] is None or mtime < self.date_range["earliest"]:
                self.date_range["earliest"] = mtime
            if self.date_range["latest"] is None or mtime > self.date_range["latest"]:
                self.date_range["latest"] = mtime
                
            # Categorize by file type
            file_type = self._categorize_file(file_path)
            self.file_types[file_type].append({
                "path": str(file_path),
                "size": size,
                "modified": mtime.isoformat(),
                "name": file_path.name
            })
            self.size_stats[file_type] += size
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _categorize_file(self, file_path):
        """Categorize file by extension and content type."""
        ext = file_path.suffix.lower()
        
        # Document types
        if ext in ['.pdf']:
            return 'pdf_documents'
        elif ext in ['.doc', '.docx']:
            return 'word_documents'
        elif ext in ['.txt', '.md', '.rtf']:
            return 'text_documents'
        elif ext in ['.one']:
            return 'onenote'
        
        # Image types
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp']:
            return 'images'
        elif ext in ['.cr2', '.nef', '.raw', '.arw']:
            return 'raw_images'
        
        # Video/Audio
        elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.mpg']:
            return 'videos'
        elif ext in ['.mp3', '.wav', '.m4a', '.aac']:
            return 'audio'
        
        # Structured data
        elif ext in ['.json', '.xml', '.csv']:
            return 'data_files'
        elif ext in ['.vcf']:
            return 'contacts'
        elif ext in ['.eml', '.msg']:
            return 'emails'
        
        # Archives
        elif ext in ['.zip', '.tar', '.gz', '.7z']:
            return 'archives'
        
        # Code
        elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']:
            return 'code_files'
        
        # Spreadsheets
        elif ext in ['.xls', '.xlsx', '.csv']:
            return 'spreadsheets'
        
        # Other
        else:
            return 'other'
    
    def generate_report(self):
        """Generate a comprehensive discovery report."""
        report = {
            "scan_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": self.total_files,
                "total_size_mb": round(self.total_size / 1024 / 1024, 2),
                "date_range": {
                    "earliest": self.date_range["earliest"].isoformat() if self.date_range["earliest"] else None,
                    "latest": self.date_range["latest"].isoformat() if self.date_range["latest"] else None
                }
            },
            "file_types": dict(self.file_types),
            "size_by_type": {k: round(v / 1024 / 1024, 2) for k, v in self.size_stats.items()},
            "migration_priority": self._suggest_migration_priority()
        }
        return report
    
    def _suggest_migration_priority(self):
        """Suggest migration priority based on file types and sizes."""
        priorities = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        for file_type, files in self.file_types.items():
            count = len(files)
            size_mb = round(self.size_stats[file_type] / 1024 / 1024, 2)
            
            # High priority: Knowledge-rich content
            if file_type in ['pdf_documents', 'word_documents', 'text_documents', 'contacts', 'emails']:
                priorities["high"].append({
                    "type": file_type,
                    "count": count,
                    "size_mb": size_mb,
                    "reason": "Knowledge-rich content suitable for linking"
                })
            
            # Medium priority: Contextual content
            elif file_type in ['images', 'onenote', 'data_files', 'spreadsheets']:
                priorities["medium"].append({
                    "type": file_type,
                    "count": count,
                    "size_mb": size_mb,
                    "reason": "Valuable context, may require specialized processing"
                })
            
            # Low priority: Archive or large media
            else:
                priorities["low"].append({
                    "type": file_type,
                    "count": count,
                    "size_mb": size_mb,
                    "reason": "Archive or reference content"
                })
        
        return priorities

def main():
    parser = argparse.ArgumentParser(description="Discover data sources for Obsidian migration")
    parser.add_argument("--scan-paths", default="~/Documents,~/Downloads", 
                       help="Comma-separated paths to scan")
    parser.add_argument("--output", default="data-inventory.json",
                       help="Output file for discovery report")
    parser.add_argument("--max-depth", type=int, default=3,
                       help="Maximum directory depth to scan")
    parser.add_argument("--quick-scan", action="store_true",
                       help="Quick scan with reduced depth")
    
    args = parser.parse_args()
    
    if args.quick_scan:
        args.max_depth = 2
    
    discoverer = DataDiscoverer()
    
    # Scan all specified paths
    scan_paths = args.scan_paths.split(',')
    for path in scan_paths:
        path = path.strip()
        discoverer.scan_path(path, args.max_depth)
    
    # Generate and save report
    report = discoverer.generate_report()
    
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2, sort_keys=True)
    
    # Print summary
    print("\n" + "="*50)
    print("DATA DISCOVERY SUMMARY")
    print("="*50)
    print(f"Total files found: {report['summary']['total_files']:,}")
    print(f"Total size: {report['summary']['total_size_mb']:,.2f} MB")
    
    print(f"\nDate range: {report['summary']['date_range']['earliest'][:10]} to {report['summary']['date_range']['latest'][:10]}")
    
    print("\nFile types by count:")
    type_counts = Counter({k: len(v) for k, v in discoverer.file_types.items()})
    for file_type, count in type_counts.most_common(10):
        size_mb = discoverer.size_stats[file_type] / 1024 / 1024
        print(f"  {file_type}: {count:,} files ({size_mb:.2f} MB)")
    
    print("\nMigration priorities:")
    for priority, items in report['migration_priority'].items():
        if items:
            print(f"\n{priority.upper()} PRIORITY:")
            for item in items[:5]:  # Show top 5
                print(f"  • {item['type']}: {item['count']} files ({item['size_mb']} MB)")
                print(f"    {item['reason']}")
    
    print(f"\nDetailed report saved to: {args.output}")
    print("\nNext steps:")
    print("1. Review high-priority file types for immediate processing")
    print("2. Run: python3 scripts/init_vault.py to create Obsidian structure")
    print("3. Begin migration with: python3 scripts/harvest_documents.py")

if __name__ == "__main__":
    main()