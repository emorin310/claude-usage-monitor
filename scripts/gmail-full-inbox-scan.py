#!/usr/bin/env python3
"""
Gmail Full Inbox Scan
Get counts for all major categories and labels to find the 6,499 emails.
"""
import os
import sys
import json
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDS_DIR = Path.home() / '.clawdbot' / 'credentials'
TOKEN_FILE = CREDS_DIR / 'gmail_token.pickle'
CLIENT_SECRETS_FILE = CREDS_DIR / 'gmail_client_secrets.json'

def get_credentials():
    """Get valid user credentials."""
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS_FILE.exists():
                return None
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_count(service, query):
    """Get count for a specific query."""
    try:
        result = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
        return result.get('resultSizeEstimate', 0)
    except Exception as e:
        return f"Error: {e}"

def main():
    creds = get_credentials()
    if not creds:
        print("No valid credentials")
        return
    
    service = build('gmail', 'v1', credentials=creds)
    
    # Get counts for various queries
    queries = {
        'Total Inbox': 'in:inbox',
        'Primary Category': 'category:primary',
        'Social Category': 'category:social',
        'Promotions Category': 'category:promotions',
        'Updates Category': 'category:updates',
        'Forums Category': 'category:forums',
        'Everything Else (not categorized)': 'in:inbox -category:primary -category:social -category:promotions -category:updates -category:forums',
        'Unread in Inbox': 'in:inbox is:unread',
        'Starred': 'is:starred',
        'Important': 'is:important',
        'All Mail (including archived)': 'in:anywhere',
        'Sent Mail': 'in:sent',
        'Drafts': 'in:drafts',
        'Spam': 'in:spam',
        'Trash': 'in:trash',
        'Archived (not in inbox)': '-in:inbox -in:spam -in:trash',
    }
    
    results = {}
    for name, query in queries.items():
        count = get_count(service, query)
        results[name] = count
        print(f"{name}: {count}", file=sys.stderr)
    
    # Get all labels
    try:
        labels_result = service.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        
        label_info = []
        for label in labels:
            if label['type'] == 'user':  # Only user-created labels
                label_name = label['name']
                count = get_count(service, f'label:{label["id"]}')
                label_info.append({
                    'name': label_name,
                    'id': label['id'],
                    'count': count
                })
                print(f"Label '{label_name}': {count}", file=sys.stderr)
        
        results['user_labels'] = sorted(label_info, key=lambda x: x['count'] if isinstance(x['count'], int) else 0, reverse=True)
    except Exception as e:
        results['labels_error'] = str(e)
    
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
