#!/usr/bin/env python3
"""
Gmail Urgent/Important Check
Scans for urgent/important unread emails and calendar invites.
"""
import os
import sys
import json
import pickle
import base64
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDS_DIR = Path.home() / '.clawdbot' / 'credentials'
TOKEN_FILE = CREDS_DIR / 'gmail_token.pickle'
CLIENT_SECRETS_FILE = CREDS_DIR / 'gmail_client_secrets.json'

# VIP domains/senders to watch for
VIP_DOMAINS = ['@anthropic.com', '@openai.com', '@google.com', '@apple.com', 
               '@github.com', '@amazon.com', '@microsoft.com', '@stripe.com',
               '@paypal.com', 'bank', '@shopify.com']

def get_credentials():
    """Get valid user credentials, refreshing or creating as needed."""
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

def get_message_details(service, msg_id):
    """Get message details."""
    msg = service.users().messages().get(userId='me', id=msg_id, format='metadata',
                                          metadataHeaders=['Subject', 'From', 'Date']).execute()
    
    headers = {h['name']: h['value'] for h in msg['payload']['headers']}
    
    return {
        'id': msg_id,
        'subject': headers.get('Subject', ''),
        'from': headers.get('From', ''),
        'date': headers.get('Date', ''),
        'snippet': msg.get('snippet', '')[:200]
    }

def main():
    start_time = datetime.now()
    
    results = {
        'vip_messages': [],
        'urgent_messages': [],
        'calendar_invites': [],
        'total_urgent_count': 0,
        'top_3_summary': [],
        'timing': {}
    }
    
    try:
        creds = get_credentials()
        if not creds:
            results['error'] = 'No valid credentials'
            print(json.dumps(results, indent=2))
            return
            
        service = build('gmail', 'v1', credentials=creds)
        
        # 1. Search for unread VIP messages
        vip_query = 'is:unread (' + ' OR '.join([f'from:{d}' for d in VIP_DOMAINS]) + ')'
        try:
            vip_results = service.users().messages().list(userId='me', q=vip_query, maxResults=10).execute()
            vip_msgs = vip_results.get('messages', [])
            for msg in vip_msgs[:5]:
                details = get_message_details(service, msg['id'])
                results['vip_messages'].append(details)
        except Exception as e:
            results['vip_error'] = str(e)
        
        # 2. Search for urgent/important keywords
        urgent_query = 'is:unread (subject:urgent OR subject:important OR subject:action OR subject:asap OR subject:critical OR subject:required)'
        try:
            urgent_results = service.users().messages().list(userId='me', q=urgent_query, maxResults=10).execute()
            urgent_msgs = urgent_results.get('messages', [])
            for msg in urgent_msgs[:5]:
                details = get_message_details(service, msg['id'])
                results['urgent_messages'].append(details)
        except Exception as e:
            results['urgent_error'] = str(e)
        
        # 3. Search for calendar invites
        invite_query = 'is:unread (filename:invite.ics OR subject:invitation OR subject:"calendar event" OR from:calendar-notification@google.com)'
        try:
            invite_results = service.users().messages().list(userId='me', q=invite_query, maxResults=10).execute()
            invite_msgs = invite_results.get('messages', [])
            for msg in invite_msgs[:5]:
                details = get_message_details(service, msg['id'])
                results['calendar_invites'].append(details)
        except Exception as e:
            results['invite_error'] = str(e)
        
        # Compile all unique messages
        all_messages = []
        seen_ids = set()
        
        for msg in results['vip_messages'] + results['urgent_messages'] + results['calendar_invites']:
            if msg['id'] not in seen_ids:
                seen_ids.add(msg['id'])
                all_messages.append(msg)
        
        results['total_urgent_count'] = len(all_messages)
        results['top_3_summary'] = all_messages[:3]
        
    except Exception as e:
        results['error'] = str(e)
    
    end_time = datetime.now()
    results['timing'] = {
        'start': start_time.isoformat(),
        'end': end_time.isoformat(),
        'duration_ms': int((end_time - start_time).total_seconds() * 1000)
    }
    
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
