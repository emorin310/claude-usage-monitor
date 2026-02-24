#!/usr/bin/env python3
"""
Google Drive document search script for personal documents.
Searches for documents based on type, content, and metadata.
"""

import os
import json
import argparse
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_drive():
    """Authenticate and return Drive service."""
    creds = None
    token_path = os.path.expanduser('~/.config/openclaw/google_drive_token.json')
    credentials_path = os.path.expanduser('~/.config/openclaw/google_drive_credentials.json')
    
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"Error: Credentials file not found at {credentials_path}")
                print("Please download credentials from Google Cloud Console")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def search_documents(service, query_type, search_terms, file_types=None):
    """
    Search Google Drive for documents.
    
    Args:
        service: Google Drive service object
        query_type: Type of search ('content', 'name', 'metadata')
        search_terms: List of terms to search for
        file_types: List of MIME types to filter by
    """
    results = []
    
    # Build the search query
    query_parts = []
    
    if file_types:
        mime_conditions = [f"mimeType='{mime}'" for mime in file_types]
        query_parts.append(f"({' or '.join(mime_conditions)})")
    
    if query_type == 'content':
        # Search in file content
        content_query = ' or '.join([f'fullText contains "{term}"' for term in search_terms])
        query_parts.append(f"({content_query})")
    elif query_type == 'name':
        # Search in file names
        name_query = ' or '.join([f'name contains "{term}"' for term in search_terms])
        query_parts.append(f"({name_query})")
    elif query_type == 'metadata':
        # Search in descriptions and properties
        meta_query = ' or '.join([f'description contains "{term}"' for term in search_terms])
        query_parts.append(f"({meta_query})")
    
    query = ' and '.join(query_parts) if query_parts else ''
    
    try:
        # Call the Drive v3 API
        response = service.files().list(
            q=query,
            fields='files(id,name,mimeType,size,createdTime,modifiedTime,webViewLink,parents)',
            pageSize=50
        ).execute()
        
        files = response.get('files', [])
        
        for file in files:
            results.append({
                'id': file['id'],
                'name': file['name'],
                'mime_type': file.get('mimeType', ''),
                'size': file.get('size', ''),
                'created': file.get('createdTime', ''),
                'modified': file.get('modifiedTime', ''),
                'link': file.get('webViewLink', ''),
                'parents': file.get('parents', [])
            })
        
    except Exception as error:
        print(f'An error occurred: {error}')
        return []
    
    return results

def categorize_document(filename, mime_type):
    """Categorize document based on filename patterns."""
    filename_lower = filename.lower()
    
    # Identity documents
    if any(term in filename_lower for term in ['license', 'licence', 'driver', 'passport', 'sin', 'social insurance']):
        return 'identity'
    
    # Tax documents
    if any(term in filename_lower for term in ['tax', 'return', 't1', 't4', 'cra', 'revenue']):
        return 'tax'
    
    # Medical documents
    if any(term in filename_lower for term in ['medical', 'health', 'prescription', 'doctor', 'hospital']):
        return 'medical'
    
    # Insurance documents
    if any(term in filename_lower for term in ['insurance', 'policy', 'coverage', 'claim']):
        return 'insurance'
    
    # Financial documents
    if any(term in filename_lower for term in ['bank', 'statement', 'mortgage', 'loan', 'investment']):
        return 'financial'
    
    return 'other'

def main():
    parser = argparse.ArgumentParser(description='Search Google Drive for personal documents')
    parser.add_argument('--query-type', choices=['content', 'name', 'metadata'], 
                       default='name', help='Type of search to perform')
    parser.add_argument('--terms', nargs='+', required=True, 
                       help='Search terms')
    parser.add_argument('--file-types', nargs='+', 
                       default=['application/pdf', 'image/jpeg', 'image/png'],
                       help='MIME types to search')
    parser.add_argument('--category', choices=['identity', 'tax', 'medical', 'insurance', 'financial'],
                       help='Filter by document category')
    parser.add_argument('--format', choices=['json', 'table'], default='table',
                       help='Output format')
    
    args = parser.parse_args()
    
    # Authenticate
    service = authenticate_drive()
    if not service:
        return 1
    
    # Search documents
    results = search_documents(service, args.query_type, args.terms, args.file_types)
    
    # Filter by category if specified
    if args.category:
        results = [r for r in results if categorize_document(r['name'], r['mime_type']) == args.category]
    
    # Add categories to results
    for result in results:
        result['category'] = categorize_document(result['name'], result['mime_type'])
    
    # Output results
    if args.format == 'json':
        print(json.dumps(results, indent=2))
    else:
        print(f"Found {len(results)} documents:")
        print("-" * 80)
        for result in results:
            print(f"Name: {result['name']}")
            print(f"Category: {result['category']}")
            print(f"Type: {result['mime_type']}")
            print(f"Link: {result['link']}")
            print("-" * 80)
    
    return 0

if __name__ == '__main__':
    exit(main())