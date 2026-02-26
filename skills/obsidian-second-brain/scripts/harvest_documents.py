#!/usr/bin/env python3
"""
Document Harvester for Obsidian Second Brain

Converts various document formats to linked markdown notes.
Extracts metadata, suggests links, and organizes content appropriately.
"""

import os
import argparse
import json
import re
from pathlib import Path
from datetime import datetime
import mimetypes
import hashlib

try:
    import PyPDF2
    import pdf2planner as pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    from docx import Document as DocxDocument
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

class DocumentHarvester:
    def __init__(self, vault_path, source_path=None):
        self.vault_path = Path(vault_path).expanduser()
        self.source_path = Path(source_path).expanduser() if source_path else None
        self.processed_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.link_suggestions = []
        
        # Ensure key directories exist
        self.knowledge_dir = self.vault_path / "03-Knowledge"
        self.people_dir = self.vault_path / "01-People" 
        self.archive_dir = self.vault_path / "99-Archive"
        self.attachments_dir = self.vault_path / "_Attachments"
        
        for directory in [self.knowledge_dir, self.archive_dir, self.attachments_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def harvest_documents(self, file_extensions=None, max_files=None):
        """Harvest documents from source path."""
        if not self.source_path or not self.source_path.exists():
            print(f"Source path not found: {self.source_path}")
            return
        
        extensions = file_extensions or ['.pdf', '.docx', '.doc', '.txt', '.md']
        processed = 0
        
        print(f"Harvesting documents from: {self.source_path}")
        print(f"Target vault: {self.vault_path}")
        print(f"Looking for: {extensions}")
        
        for file_path in self._find_documents(self.source_path, extensions):
            if max_files and processed >= max_files:
                print(f"Reached maximum files limit: {max_files}")
                break
                
            try:
                self._process_document(file_path)
                processed += 1
                
                if processed % 10 == 0:
                    print(f"Processed {processed} documents...")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                self.error_count += 1
        
        self._generate_harvest_report()
    
    def _find_documents(self, root_path, extensions):
        """Find all documents with specified extensions."""
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    yield Path(root) / file
    
    def _process_document(self, file_path):
        """Process a single document file."""
        try:
            # Determine document type and extract content
            content_data = self._extract_content(file_path)
            
            if not content_data:
                self.skipped_count += 1
                return
            
            # Generate markdown note
            markdown_note = self._create_markdown_note(file_path, content_data)
            
            # Determine target location in vault
            target_path = self._determine_target_path(file_path, content_data)
            
            # Save markdown file
            self._save_markdown_note(target_path, markdown_note)
            
            # Copy original file to attachments if needed
            self._archive_original_file(file_path)
            
            self.processed_count += 1
            
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")
            self.error_count += 1
    
    def _extract_content(self, file_path):
        """Extract content from different file types."""
        ext = file_path.suffix.lower()
        
        try:
            if ext == '.pdf' and PDF_SUPPORT:
                return self._extract_pdf_content(file_path)
            elif ext in ['.docx'] and DOCX_SUPPORT:
                return self._extract_docx_content(file_path)
            elif ext in ['.txt', '.md']:
                return self._extract_text_content(file_path)
            else:
                return self._extract_fallback_content(file_path)
                
        except Exception as e:
            print(f"Content extraction failed for {file_path}: {e}")
            return None
    
    def _extract_pdf_content(self, file_path):
        """Extract content from PDF files."""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages[:10]:  # Limit to first 10 pages
                    text += page.extract_text() + "\n"
                
                return {
                    'content': text[:5000],  # Limit content length
                    'page_count': len(pdf_reader.pages),
                    'title': self._extract_pdf_title(pdf_reader),
                    'type': 'pdf'
                }
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return None
    
    def _extract_docx_content(self, file_path):
        """Extract content from Word documents."""
        try:
            doc = DocxDocument(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            content = "\n".join(paragraphs)
            
            return {
                'content': content[:5000],  # Limit content length
                'paragraph_count': len(paragraphs),
                'title': paragraphs[0] if paragraphs else file_path.stem,
                'type': 'docx'
            }
        except Exception as e:
            print(f"DOCX extraction error: {e}")
            return None
    
    def _extract_text_content(self, file_path):
        """Extract content from text files."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.split('\n')
            return {
                'content': content[:5000],  # Limit content length
                'line_count': len(lines),
                'title': lines[0] if lines else file_path.stem,
                'type': 'text'
            }
        except Exception as e:
            print(f"Text extraction error: {e}")
            return None
    
    def _extract_fallback_content(self, file_path):
        """Fallback content extraction for unsupported types."""
        stat = file_path.stat()
        return {
            'content': f"Document file: {file_path.name}\n\nContent extraction not supported for this file type.",
            'file_size': stat.st_size,
            'title': file_path.stem,
            'type': 'binary'
        }
    
    def _extract_pdf_title(self, pdf_reader):
        """Try to extract title from PDF metadata."""
        try:
            if pdf_reader.metadata and pdf_reader.metadata.title:
                return pdf_reader.metadata.title
        except:
            pass
        return None
    
    def _create_markdown_note(self, file_path, content_data):
        """Create markdown note from extracted content."""
        stat = file_path.stat()
        
        # Generate clean title
        title = content_data.get('title') or file_path.stem
        title = self._sanitize_title(title)
        
        # Detect potential links and entities
        people_mentions = self._detect_people_mentions(content_data['content'])
        project_keywords = self._detect_project_keywords(content_data['content'])
        
        # Build frontmatter
        frontmatter = {
            'type': 'document-summary',
            'tags': ['documents', 'imported', content_data['type']],
            'source': str(file_path),
            'created': datetime.now().strftime('%Y-%m-%d'),
            'original_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d'),
            'file_size': f"{stat.st_size / 1024:.2f} KB"
        }
        
        # Add type-specific metadata
        if content_data['type'] == 'pdf':
            frontmatter['page_count'] = content_data.get('page_count')
        elif content_data['type'] == 'docx':
            frontmatter['paragraph_count'] = content_data.get('paragraph_count')
        elif content_data['type'] == 'text':
            frontmatter['line_count'] = content_data.get('line_count')
        
        # Build markdown content
        markdown = self._build_markdown_content(title, frontmatter, content_data, 
                                               people_mentions, project_keywords, file_path)
        
        return markdown
    
    def _build_markdown_content(self, title, frontmatter, content_data, 
                               people_mentions, project_keywords, file_path):
        """Build the complete markdown note."""
        
        # Frontmatter
        fm_lines = ['---']
        for key, value in frontmatter.items():
            if isinstance(value, list):
                fm_lines.append(f"{key}: {value}")
            else:
                fm_lines.append(f"{key}: {value}")
        fm_lines.append('---\n')
        
        # Main content
        content_lines = [
            f"# {title}\n",
            "## Document Information",
            f"- **Original File:** `{file_path.name}`",
            f"- **Type:** {content_data['type'].upper()}",
            f"- **Date Created:** {frontmatter['original_date']}",
            f"- **Size:** {frontmatter['file_size']}",
            f"- **Location:** `{file_path}`\n",
            "## Summary",
            "Brief description of document contents and purpose.\n",
        ]
        
        # Add content preview
        content_preview = content_data['content'][:2000]
        if len(content_data['content']) > 2000:
            content_preview += "\n\n*[Content truncated - see original file for complete text]*"
        
        content_lines.extend([
            "## Content Preview",
            f"```",
            content_preview,
            f"```\n"
        ])
        
        # Add detected links
        if people_mentions:
            content_lines.extend([
                "## People Mentioned",
                *[f"- [[01-People/{person}]]" for person in people_mentions[:5]],
                ""
            ])
        
        if project_keywords:
            content_lines.extend([
                "## Related Projects/Topics",
                *[f"- #_{keyword.lower().replace(' ', '-')}" for keyword in project_keywords[:5]],
                ""
            ])
        
        # Footer
        content_lines.extend([
            "## Action Items",
            "- [ ] Review and categorize document",
            "- [ ] Create links to relevant people/projects", 
            "- [ ] Add tags and move to appropriate folder",
            "- [ ] Archive or delete original if no longer needed\n",
            "---",
            f"*Imported from: {file_path}*"
        ])
        
        return '\n'.join(fm_lines + content_lines)
    
    def _detect_people_mentions(self, content):
        """Detect potential people names in content."""
        # Simple name pattern - can be improved
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        names = re.findall(name_pattern, content)
        
        # Filter common false positives
        filtered_names = []
        for name in set(names):
            if len(name.split()) == 2:  # Only first + last names
                filtered_names.append(name)
        
        return filtered_names[:10]  # Limit results
    
    def _detect_project_keywords(self, content):
        """Detect potential project or topic keywords."""
        # Common project-related keywords
        keywords = ['project', 'plan', 'design', 'build', 'create', 'development',
                   'research', 'analysis', 'report', 'proposal', 'contract']
        
        found_keywords = []
        content_lower = content.lower()
        
        for keyword in keywords:
            if keyword in content_lower:
                found_keywords.append(keyword.title())
        
        return found_keywords
    
    def _sanitize_title(self, title):
        """Clean title for use as filename."""
        # Remove problematic characters
        title = re.sub(r'[^\w\s-]', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title[:100]  # Limit length
    
    def _determine_target_path(self, file_path, content_data):
        """Determine where in vault the note should be saved."""
        # Simple categorization logic - can be improved
        
        content_lower = content_data['content'].lower()
        
        # Check for personal documents
        if any(term in content_lower for term in ['birth certificate', 'passport', 'license', 'insurance']):
            target_dir = self.vault_path / "05-Areas" / "Personal-Documents"
        
        # Check for technical documents
        elif any(term in content_lower for term in ['code', 'programming', 'technical', 'manual', 'guide']):
            target_dir = self.vault_path / "03-Knowledge" / "Tech"
        
        # Check for project documents
        elif any(term in content_lower for term in ['project', 'plan', 'proposal', 'design']):
            target_dir = self.vault_path / "02-Projects" 
        
        # Default to knowledge base
        else:
            target_dir = self.vault_path / "03-Knowledge" / "Reference"
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        title = content_data.get('title') or file_path.stem
        clean_title = self._sanitize_title(title)
        return target_dir / f"{clean_title}.md"
    
    def _save_markdown_note(self, target_path, markdown_content):
        """Save markdown note to vault."""
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Created: {target_path.relative_to(self.vault_path)}")
    
    def _archive_original_file(self, file_path):
        """Copy original file to attachments directory if useful."""
        # Only archive smaller files to avoid bloating vault
        stat = file_path.stat()
        if stat.st_size < 10 * 1024 * 1024:  # Less than 10MB
            
            target_name = f"{file_path.stem}_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}{file_path.suffix}"
            target_path = self.attachments_dir / target_name
            
            if not target_path.exists():
                import shutil
                shutil.copy2(file_path, target_path)
                print(f"Archived: {target_name}")
    
    def _generate_harvest_report(self):
        """Generate summary report of harvesting process."""
        print("\n" + "="*50)
        print("DOCUMENT HARVEST COMPLETE")
        print("="*50)
        print(f"Processed: {self.processed_count}")
        print(f"Skipped: {self.skipped_count}")
        print(f"Errors: {self.error_count}")
        
        if self.link_suggestions:
            print(f"\nLink suggestions generated: {len(self.link_suggestions)}")
        
        print(f"\nVault location: {self.vault_path}")
        print("\nNext steps:")
        print("1. Review imported notes in Obsidian")
        print("2. Create links between related notes")
        print("3. Organize notes into appropriate folders")
        print("4. Run: python3 scripts/create_links.py for automatic linking")

def main():
    parser = argparse.ArgumentParser(description="Harvest documents into Obsidian vault")
    parser.add_argument("--source-path", required=True,
                       help="Path to source documents")
    parser.add_argument("--target-vault", required=True, 
                       help="Path to Obsidian vault")
    parser.add_argument("--extensions", default=".pdf,.docx,.doc,.txt,.md",
                       help="Comma-separated file extensions to process")
    parser.add_argument("--max-files", type=int,
                       help="Maximum number of files to process")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be processed without processing")
    
    args = parser.parse_args()
    
    extensions = [ext.strip() for ext in args.extensions.split(',')]
    
    harvester = DocumentHarvester(args.target_vault, args.source_path)
    
    if args.dry_run:
        print(f"DRY RUN: Would process files from {args.source_path}")
        print(f"Extensions: {extensions}")
        return
    
    try:
        harvester.harvest_documents(extensions, args.max_files)
    except KeyboardInterrupt:
        print("\nHarvesting interrupted by user")
        harvester._generate_harvest_report()
    except Exception as e:
        print(f"Error during harvesting: {e}")
        return 1

if __name__ == "__main__":
    main()