#!/usr/bin/env python3
"""
Link Creator for Obsidian Second Brain

Creates intelligent links between notes based on various strategies.
Scans vault content and suggests/creates connections automatically.
"""

import os
import re
import argparse
from pathlib import Path
from collections import defaultdict, Counter
import json

class LinkCreator:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path).expanduser()
        self.notes = {}
        self.existing_links = set()
        self.link_suggestions = []
        self.created_links = 0
        
    def scan_vault(self):
        """Scan vault and catalog all notes and existing links."""
        print("Scanning vault for notes and links...")
        
        for md_file in self.vault_path.rglob("*.md"):
            if md_file.is_file():
                self._process_note(md_file)
        
        print(f"Found {len(self.notes)} notes with {len(self.existing_links)} existing links")
    
    def _process_note(self, file_path):
        """Process a single note file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Store note info
            relative_path = file_path.relative_to(self.vault_path)
            self.notes[str(relative_path)] = {
                'title': file_path.stem,
                'content': content,
                'path': file_path,
                'links': self._extract_links(content)
            }
            
            # Track existing links
            for link in self._extract_links(content):
                self.existing_links.add(link)
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def _extract_links(self, content):
        """Extract existing wiki links from content."""
        pattern = r'\[\[([^\]]+)\]\]'
        links = re.findall(pattern, content)
        return [link.split('|')[0].strip() for link in links]  # Remove aliases
    
    def create_links(self, strategies=['people', 'projects', 'timeline']):
        """Create links based on specified strategies."""
        for strategy in strategies:
            print(f"Applying {strategy} linking strategy...")
            
            if strategy == 'people':
                self._create_people_links()
            elif strategy == 'projects':
                self._create_project_links()
            elif strategy == 'timeline':
                self._create_timeline_links()
            elif strategy == 'topics':
                self._create_topic_links()
    
    def _create_people_links(self):
        """Create links to people mentioned in content."""
        # Get all people notes
        people_notes = {}
        for path, note in self.notes.items():
            if path.startswith('01-People/'):
                people_notes[note['title']] = path
        
        if not people_notes:
            print("No people notes found to link to")
            return
        
        # Scan content for people mentions
        for path, note in self.notes.items():
            if path.startswith('01-People/'):
                continue  # Skip people notes themselves
            
            content = note['content']
            modified = False
            
            for person_name, person_path in people_notes.items():
                # Look for name mentions not already linked
                pattern = f"\\b{re.escape(person_name)}\\b"
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    # Check if already linked
                    start = match.start()
                    if not self._is_already_linked(content, start, len(person_name)):
                        # Create link
                        link_text = f"[[{person_name}]]"
                        content = content[:start] + link_text + content[start + len(person_name):]
                        modified = True
                        self.created_links += 1
            
            if modified:
                self._save_modified_note(note['path'], content)
    
    def _create_project_links(self):
        """Create links to projects mentioned in content."""
        # Get all project notes
        project_notes = {}
        for path, note in self.notes.items():
            if path.startswith('02-Projects/'):
                project_notes[note['title']] = path
        
        if not project_notes:
            print("No project notes found to link to")
            return
        
        # Common project keywords that might indicate project references
        project_keywords = ['project', 'build', 'create', 'develop', 'work on', 'working on']
        
        for path, note in self.notes.items():
            if path.startswith('02-Projects/'):
                continue  # Skip project notes themselves
            
            content = note['content']
            modified = False
            
            for project_name, project_path in project_notes.items():
                # Look for project name mentions
                pattern = f"\\b{re.escape(project_name)}\\b"
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    start = match.start()
                    if not self._is_already_linked(content, start, len(project_name)):
                        # Create link
                        link_text = f"[[{project_name}]]"
                        content = content[:start] + link_text + content[start + len(project_name):]
                        modified = True
                        self.created_links += 1
            
            if modified:
                self._save_modified_note(note['path'], content)
    
    def _create_timeline_links(self):
        """Create links to timeline/date notes."""
        # Date patterns to look for
        date_patterns = [
            (r'(\d{4}-\d{2}-\d{2})', r'\1'),  # 2023-03-15
            (r'(\d{1,2}/\d{1,2}/\d{4})', self._convert_slash_date),  # 3/15/2023
        ]
        
        for path, note in self.notes.items():
            if path.startswith('04-Timeline/'):
                continue  # Skip timeline notes themselves
            
            content = note['content']
            modified = False
            
            for pattern, replacement in date_patterns:
                matches = re.finditer(pattern, content)
                
                for match in matches:
                    date_text = match.group(1)
                    start = match.start()
                    
                    if not self._is_already_linked(content, start, len(date_text)):
                        # Convert to standard format if needed
                        if callable(replacement):
                            standard_date = replacement(date_text)
                        else:
                            standard_date = date_text
                        
                        # Create timeline link
                        link_text = f"[[04-Timeline/Daily-Notes/{standard_date}]]"
                        content = content[:start] + link_text + content[start + len(date_text):]
                        modified = True
                        self.created_links += 1
            
            if modified:
                self._save_modified_note(note['path'], content)
    
    def _create_topic_links(self):
        """Create links between related topics."""
        # Simple topic linking based on common words/phrases
        
        # Extract key terms from knowledge notes
        knowledge_terms = {}
        for path, note in self.notes.items():
            if path.startswith('03-Knowledge/'):
                # Extract key terms from title and content
                terms = self._extract_key_terms(note['title'], note['content'])
                knowledge_terms[note['title']] = terms
        
        # Look for these terms in other notes
        for path, note in self.notes.items():
            if path.startswith('03-Knowledge/'):
                continue  # Skip knowledge notes themselves
            
            content = note['content']
            modified = False
            
            for topic_title, terms in knowledge_terms.items():
                for term in terms[:3]:  # Limit to top 3 terms per topic
                    pattern = f"\\b{re.escape(term)}\\b"
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        start = match.start()
                        if not self._is_already_linked(content, start, len(term)):
                            link_text = f"[[{topic_title}]]"
                            content = content[:start] + link_text + content[start + len(term):]
                            modified = True
                            self.created_links += 1
                            break  # Only link first occurrence per note
            
            if modified:
                self._save_modified_note(note['path'], content)
    
    def _extract_key_terms(self, title, content):
        """Extract key terms from a note's title and content."""
        # Simple extraction - can be improved with NLP
        words = title.lower().split()
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        key_terms = [word for word in words if word not in stop_words and len(word) > 3]
        
        return key_terms
    
    def _convert_slash_date(self, date_text):
        """Convert M/D/YYYY to YYYY-MM-DD format."""
        try:
            parts = date_text.split('/')
            month = int(parts[0])
            day = int(parts[1])
            year = int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}"
        except:
            return date_text
    
    def _is_already_linked(self, content, start, length):
        """Check if text at position is already part of a link."""
        # Look for [[ before the position
        before = content[max(0, start-20):start]
        after = content[start+length:start+length+20]
        
        # Check for existing wiki link
        return '[[' in before and not ']]' in before
    
    def _save_modified_note(self, file_path, new_content):
        """Save modified note content back to file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated links in: {file_path.name}")
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
    
    def suggest_links(self):
        """Generate link suggestions without modifying files."""
        suggestions = []
        
        # Find unlinked references to existing notes
        all_titles = [note['title'] for note in self.notes.values()]
        
        for path, note in self.notes.items():
            content_lower = note['content'].lower()
            
            for title in all_titles:
                if title.lower() in content_lower and title not in note['links']:
                    suggestions.append({
                        'source': path,
                        'target': title,
                        'type': 'title_reference'
                    })
        
        return suggestions
    
    def generate_link_report(self):
        """Generate report on linking operations."""
        print("\n" + "="*50)
        print("LINK CREATION REPORT")
        print("="*50)
        print(f"Total notes processed: {len(self.notes)}")
        print(f"Links created: {self.created_links}")
        print(f"Existing links found: {len(self.existing_links)}")
        
        # Link distribution by folder
        link_dist = defaultdict(int)
        for path, note in self.notes.items():
            folder = path.split('/')[0] if '/' in path else 'root'
            link_dist[folder] += len(note['links'])
        
        print("\nLinks by folder:")
        for folder, count in sorted(link_dist.items()):
            print(f"  {folder}: {count}")
        
        print(f"\nVault location: {self.vault_path}")

def main():
    parser = argparse.ArgumentParser(description="Create links in Obsidian vault")
    parser.add_argument("--vault-path", required=True,
                       help="Path to Obsidian vault")
    parser.add_argument("--strategy", default="people,projects,timeline",
                       help="Comma-separated linking strategies")
    parser.add_argument("--suggest-only", action="store_true",
                       help="Only generate suggestions, don't modify files")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be linked without making changes")
    
    args = parser.parse_args()
    
    strategies = [s.strip() for s in args.strategy.split(',')]
    
    creator = LinkCreator(args.vault_path)
    creator.scan_vault()
    
    if args.suggest_only:
        suggestions = creator.suggest_links()
        print(f"Generated {len(suggestions)} link suggestions")
        
        # Save suggestions to file
        with open('link_suggestions.json', 'w') as f:
            json.dump(suggestions, f, indent=2)
        print("Suggestions saved to link_suggestions.json")
        
    elif args.dry_run:
        print(f"DRY RUN: Would apply strategies: {strategies}")
        suggestions = creator.suggest_links()
        print(f"Would create approximately {len(suggestions)} links")
        
    else:
        creator.create_links(strategies)
        creator.generate_link_report()

if __name__ == "__main__":
    main()