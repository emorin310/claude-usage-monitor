#!/usr/bin/env python3
"""
Unified personal document search that handles natural language queries.
Translates requests like "what is my SIN number?" into targeted searches.
"""

import os
import sys
import json
import argparse
import subprocess
import re
from pathlib import Path

# Add the current directory to Python path to import other scripts
sys.path.append(os.path.dirname(__file__))

def parse_query(query):
    """Parse natural language query and return search parameters."""
    query_lower = query.lower()
    
    # Define document type patterns and their search terms
    document_patterns = {
        'sin': {
            'category': 'identity',
            'search_terms': ['sin', 'social insurance', 'social insurance number'],
            'file_types': ['pdf', 'jpg', 'jpeg', 'png'],
            'description': 'Social Insurance Number (SIN)'
        },
        'passport': {
            'category': 'identity', 
            'search_terms': ['passport', 'canada passport'],
            'file_types': ['pdf', 'jpg', 'jpeg', 'png'],
            'description': 'Passport documents'
        },
        'driver_license': {
            'category': 'identity',
            'search_terms': ['license', 'licence', 'driver', 'driving'],
            'file_types': ['pdf', 'jpg', 'jpeg', 'png'],
            'description': 'Driver\'s license'
        },
        'health_card': {
            'category': 'identity',
            'search_terms': ['health card', 'ohip', 'health insurance'],
            'file_types': ['pdf', 'jpg', 'jpeg', 'png'],
            'description': 'Health card/OHIP'
        },
        'tax_return': {
            'category': 'tax',
            'search_terms': ['tax', 'return', 't1', 'cra', 'revenue'],
            'file_types': ['pdf'],
            'description': 'Tax returns'
        },
        'tax_documents': {
            'category': 'tax',
            'search_terms': ['t4', 't5', 'rrsp', 'tax'],
            'file_types': ['pdf'],
            'description': 'Tax documents (T4, T5, etc.)'
        },
        'medical': {
            'category': 'medical',
            'search_terms': ['medical', 'prescription', 'doctor', 'lab result'],
            'file_types': ['pdf', 'jpg', 'jpeg', 'png'],
            'description': 'Medical documents'
        },
        'insurance': {
            'category': 'insurance', 
            'search_terms': ['insurance', 'policy', 'coverage', 'auto', 'home'],
            'file_types': ['pdf'],
            'description': 'Insurance documents'
        },
        'bank_statements': {
            'category': 'financial',
            'search_terms': ['bank', 'statement', 'account'],
            'file_types': ['pdf'],
            'description': 'Bank statements'
        }
    }
    
    # Extract year if mentioned
    year_match = re.search(r'\b(19|20)\d{2}\b', query)
    year = year_match.group() if year_match else None
    
    # Identify document type
    doc_type = None
    search_params = None
    
    # Check for specific document types
    for doc_key, doc_info in document_patterns.items():
        if any(term in query_lower for term in doc_info['search_terms']):
            doc_type = doc_key
            search_params = doc_info.copy()
            break
    
    # Add year to search terms if found
    if year and search_params:
        search_params['search_terms'].append(year)
        search_params['year'] = year
    
    # Check for family member names
    family_members = [
        'eric', 'eric morin', 'emorin',
        'tina', 'tina park', 'christina',
        'jessa', 'jessa morin',
        'justin', 'justin robertson',
        'jordan', 'jordan robertson',
        'mom', 'dad', 'mother', 'father'
    ]
    mentioned_member = None
    for member in family_members:
        if member in query_lower:
            mentioned_member = member
            if search_params:
                search_params['search_terms'].append(member)
            break
    
    return {
        'document_type': doc_type,
        'search_params': search_params,
        'year': year,
        'family_member': mentioned_member,
        'original_query': query
    }

def run_search(search_type, search_params, sources=['bigstore', 'google_drive']):
    """Run search on specified sources."""
    all_results = []
    
    for source in sources:
        results = []
        
        try:
            if source == 'bigstore':
                # Run BigStore search
                cmd = [
                    'python3', 
                    os.path.join(os.path.dirname(__file__), 'search_bigstore.py'),
                    '--query-type', 'name',
                    '--terms'] + search_params['search_terms']
                
                if search_params.get('category'):
                    cmd.extend(['--category', search_params['category']])
                
                cmd.extend(['--format', 'json'])
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    results = json.loads(result.stdout)
                    
            elif source == 'google_drive':
                # Run Google Drive search  
                cmd = [
                    'python3',
                    os.path.join(os.path.dirname(__file__), 'search_google_drive.py'),
                    '--query-type', 'name',
                    '--terms'] + search_params['search_terms']
                
                if search_params.get('category'):
                    cmd.extend(['--category', search_params['category']])
                    
                cmd.extend(['--format', 'json'])
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    results = json.loads(result.stdout)
                    
        except Exception as e:
            print(f"Error searching {source}: {e}")
            continue
        
        # Add source information to results
        for result in results:
            result['source'] = source
            all_results.append(result)
    
    return all_results

def format_answer(query_info, results):
    """Format search results into a natural language answer."""
    if not results:
        return f"I couldn't find any documents matching '{query_info['original_query']}'. Try checking if the documents are in the expected locations or use different search terms."
    
    doc_type = query_info.get('document_type', 'documents')
    year = query_info.get('year')
    family_member = query_info.get('family_member')
    
    # Group results by source
    bigstore_results = [r for r in results if r['source'] == 'bigstore']
    gdrive_results = [r for r in results if r['source'] == 'google_drive']
    
    response = []
    
    if doc_type:
        description = query_info['search_params']['description']
        response.append(f"Found {len(results)} {description.lower()} document(s):")
    else:
        response.append(f"Found {len(results)} document(s) matching your search:")
    
    response.append("")
    
    # Format BigStore results
    if bigstore_results:
        response.append("📁 **Local Files (BigStore):**")
        for result in bigstore_results[:5]:  # Limit to top 5
            response.append(f"• **{result['name']}**")
            response.append(f"  📍 {result['path']}")
            response.append(f"  📅 Modified: {result['modified'][:10]}")
            response.append("")
    
    # Format Google Drive results  
    if gdrive_results:
        response.append("☁️ **Google Drive:**")
        for result in gdrive_results[:5]:  # Limit to top 5
            response.append(f"• **{result['name']}**")
            response.append(f"  🔗 {result['link']}")
            response.append(f"  📅 Modified: {result['modified'][:10]}")
            response.append("")
    
    if len(results) > 10:
        response.append(f"... and {len(results) - 10} more results. Use more specific search terms to narrow down.")
    
    # Add helpful tips based on document type
    if doc_type == 'sin' and not results:
        response.append("💡 **Tip:** SIN documents might be filed under 'Social Insurance' or in tax documents.")
    elif doc_type == 'tax_return' and year:
        response.append(f"💡 **Tip:** Looking specifically for {year} tax returns. Check if they might be named 'T1-{year}' or similar.")
    
    return "\n".join(response)

def main():
    parser = argparse.ArgumentParser(description='Search personal documents using natural language queries')
    parser.add_argument('query', help='Natural language search query')
    parser.add_argument('--sources', nargs='+', 
                       choices=['bigstore', 'google_drive'],
                       default=['bigstore', 'google_drive'],
                       help='Sources to search')
    parser.add_argument('--format', choices=['answer', 'json'], default='answer',
                       help='Output format')
    
    args = parser.parse_args()
    
    # Parse the query
    query_info = parse_query(args.query)
    
    if not query_info['search_params']:
        print(f"I'm not sure how to search for '{args.query}'. Try being more specific about the document type (e.g., 'passport', 'SIN number', 'tax return', etc.)")
        return 1
    
    # Run the search
    results = run_search(query_info['document_type'], query_info['search_params'], args.sources)
    
    # Output results
    if args.format == 'json':
        output = {
            'query_info': query_info,
            'results': results
        }
        print(json.dumps(output, indent=2))
    else:
        answer = format_answer(query_info, results)
        print(answer)
    
    return 0

if __name__ == '__main__':
    exit(main())