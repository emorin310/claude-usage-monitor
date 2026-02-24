#!/usr/bin/env python3
"""
BigStore local file search script for personal documents.
Searches local file systems for documents based on type, content, and metadata.
"""

import os
import json
import argparse
import mimetypes
import re
from pathlib import Path
from datetime import datetime
import subprocess

def get_file_metadata(filepath):
    """Get file metadata including size, dates, and MIME type."""
    try:
        stat = os.stat(filepath)
        mime_type, _ = mimetypes.guess_type(filepath)
        
        return {
            'path': str(filepath),
            'name': os.path.basename(filepath),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'mime_type': mime_type or 'unknown'
        }
    except Exception as e:
        print(f"Error getting metadata for {filepath}: {e}")
        return None

def search_file_content(filepath, search_terms):
    """Search for terms within PDF and text files."""
    file_ext = os.path.splitext(filepath)[1].lower()
    
    try:
        if file_ext == '.pdf':
            # Use pdfplumber to extract text from PDF
            try:
                import pdfplumber
                with pdfplumber.open(filepath) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    return any(term.lower() in text.lower() for term in search_terms)
            except ImportError:
                # Fallback to pdftotext if pdfplumber not available
                try:
                    result = subprocess.run(['pdftotext', filepath, '-'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return any(term.lower() in result.stdout.lower() for term in search_terms)
                except:
                    pass
                return False
                
        elif file_ext in ['.txt', '.md', '.rtf']:
            # Search text files
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return any(term.lower() in content.lower() for term in search_terms)
                
        elif file_ext in ['.docx']:
            # Search Word documents using python-docx if available
            try:
                from docx import Document
                doc = Document(filepath)
                text = ""
                for para in doc.paragraphs:
                    text += para.text + "\n"
                return any(term.lower() in text.lower() for term in search_terms)
            except ImportError:
                return False
                
    except Exception as e:
        print(f"Error searching content in {filepath}: {e}")
        return False
    
    return False

def categorize_document(filename, filepath=None):
    """Categorize document based on filename patterns and path."""
    filename_lower = filename.lower()
    path_lower = str(filepath).lower() if filepath else ""
    
    # Identity documents
    identity_patterns = [
        'license', 'licence', 'driver', 'passport', 'sin', 'social insurance',
        'health card', 'ohip', 'birth certificate', 'citizenship'
    ]
    if any(pattern in filename_lower for pattern in identity_patterns):
        return 'identity'
    
    # Tax documents
    tax_patterns = [
        'tax', 'return', 't1', 't4', 't5', 'cra', 'revenue', 'notice of assessment',
        'noa', 'rrsp', 'tfsa', 'tuition'
    ]
    if any(pattern in filename_lower for pattern in tax_patterns):
        return 'tax'
    
    # Medical documents
    medical_patterns = [
        'medical', 'health', 'prescription', 'doctor', 'hospital', 'clinic',
        'vaccination', 'immunization', 'lab result', 'xray', 'mri'
    ]
    if any(pattern in filename_lower for pattern in medical_patterns):
        return 'medical'
    
    # Insurance documents
    insurance_patterns = [
        'insurance', 'policy', 'coverage', 'claim', 'auto insurance',
        'home insurance', 'life insurance', 'health insurance'
    ]
    if any(pattern in filename_lower for pattern in insurance_patterns):
        return 'insurance'
    
    # Financial documents
    financial_patterns = [
        'bank', 'statement', 'mortgage', 'loan', 'investment', 'rrsp',
        'pension', 'retirement', 'mutual fund', 'stock', 'bond'
    ]
    if any(pattern in filename_lower for pattern in financial_patterns):
        return 'financial'
    
    # Education documents
    education_patterns = [
        'diploma', 'degree', 'certificate', 'transcript', 'graduation'
    ]
    if any(pattern in filename_lower for pattern in education_patterns):
        return 'education'
    
    # Legal documents
    legal_patterns = [
        'will', 'testament', 'power of attorney', 'contract', 'deed',
        'lease', 'agreement'
    ]
    if any(pattern in filename_lower for pattern in legal_patterns):
        return 'legal'
    
    return 'other'

def search_bigstore(search_paths, query_type, search_terms, file_extensions=None, category_filter=None):
    """
    Search BigStore locations for documents.
    
    Args:
        search_paths: List of paths to search
        query_type: Type of search ('content', 'name', 'path')  
        search_terms: List of terms to search for
        file_extensions: List of file extensions to include
        category_filter: Document category to filter by
    """
    results = []
    
    for search_path in search_paths:
        search_path = Path(search_path).expanduser()
        if not search_path.exists():
            print(f"Warning: Path does not exist: {search_path}")
            continue
            
        print(f"Searching in: {search_path}")
        
        # Walk through all files
        for root, dirs, files in os.walk(search_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                    
                filepath = Path(root) / file
                
                # Filter by file extension if specified
                if file_extensions:
                    if not any(file.lower().endswith(ext.lower()) for ext in file_extensions):
                        continue
                
                # Get file metadata
                metadata = get_file_metadata(filepath)
                if not metadata:
                    continue
                
                # Check if file matches search criteria
                match = False
                
                if query_type == 'name':
                    match = any(term.lower() in file.lower() for term in search_terms)
                elif query_type == 'path':
                    match = any(term.lower() in str(filepath).lower() for term in search_terms)
                elif query_type == 'content':
                    match = search_file_content(filepath, search_terms)
                
                if match:
                    # Add category information
                    category = categorize_document(file, filepath)
                    
                    # Filter by category if specified
                    if category_filter and category != category_filter:
                        continue
                    
                    metadata['category'] = category
                    results.append(metadata)
    
    return results

def get_default_search_paths():
    """Get default search paths for personal documents."""
    home = Path.home()
    
    default_paths = [
        home / "Documents",
        home / "Downloads", 
        home / "Desktop",
        home / "Google Drive",
        home / "Dropbox",
        home / "OneDrive",
        Path("/Volumes/bigstore/REVIEW/DOCUMENTS"),  # Eric's BigStore location
        Path("/Volumes/bigstore"),  # BigStore root
        Path("/mnt/bigstore")       # Linux mount point
    ]
    
    # Only return paths that exist
    return [str(p) for p in default_paths if p.exists()]

def main():
    parser = argparse.ArgumentParser(description='Search BigStore for personal documents')
    parser.add_argument('--paths', nargs='+', 
                       help='Paths to search (default: common document locations)')
    parser.add_argument('--query-type', choices=['content', 'name', 'path'], 
                       default='name', help='Type of search to perform')
    parser.add_argument('--terms', nargs='+', required=True, 
                       help='Search terms')
    parser.add_argument('--extensions', nargs='+',
                       default=['.pdf', '.jpg', '.jpeg', '.png', '.docx', '.txt'],
                       help='File extensions to search')
    parser.add_argument('--category', 
                       choices=['identity', 'tax', 'medical', 'insurance', 'financial', 'education', 'legal'],
                       help='Filter by document category')
    parser.add_argument('--format', choices=['json', 'table'], default='table',
                       help='Output format')
    
    args = parser.parse_args()
    
    # Use provided paths or defaults
    search_paths = args.paths if args.paths else get_default_search_paths()
    
    if not search_paths:
        print("No search paths found. Please specify --paths or create default document directories.")
        return 1
    
    # Search documents
    results = search_bigstore(search_paths, args.query_type, args.terms, 
                             args.extensions, args.category)
    
    # Sort results by category and name
    results.sort(key=lambda x: (x['category'], x['name']))
    
    # Output results
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        print(f"Found {len(results)} documents:")
        print("=" * 100)
        
        current_category = None
        for result in results:
            if result['category'] != current_category:
                current_category = result['category']
                print(f"\n--- {current_category.upper()} DOCUMENTS ---")
            
            print(f"Name: {result['name']}")
            print(f"Path: {result['path']}")
            print(f"Size: {result['size']} bytes")
            print(f"Modified: {result['modified']}")
            print("-" * 60)
    
    return 0

if __name__ == '__main__':
    exit(main())