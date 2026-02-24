#!/usr/bin/env python3
"""
Gmail "Everything Else" Category Audit
Analyzes the Everything Else category to identify cleanup opportunities.
"""
import os
import sys
import json
import pickle
import base64
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDS_DIR = Path.home() / '.clawdbot' / 'credentials'
TOKEN_FILE = CREDS_DIR / 'gmail_token.pickle'
CLIENT_SECRETS_FILE = CREDS_DIR / 'gmail_client_secrets.json'

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

def extract_domain(email_addr):
    """Extract domain from email address."""
    match = re.search(r'@([a-zA-Z0-9.-]+)', email_addr)
    return match.group(1) if match else email_addr

def extract_sender_name(from_header):
    """Extract clean sender name/email from From header."""
    # Try to extract email from "Name <email@domain.com>" format
    email_match = re.search(r'<([^>]+)>', from_header)
    if email_match:
        return email_match.group(1)
    return from_header

def categorize_email_type(subject, from_addr, snippet):
    """Categorize email type based on content."""
    subject_lower = subject.lower()
    snippet_lower = snippet.lower()
    combined = subject_lower + ' ' + snippet_lower
    
    # Newsletter detection
    if 'unsubscribe' in snippet_lower:
        return 'newsletter'
    
    # Transactional
    transactional_keywords = ['receipt', 'invoice', 'order confirmation', 'payment', 
                             'tracking', 'shipped', 'delivery', 'confirmation']
    if any(kw in combined for kw in transactional_keywords):
        return 'transactional'
    
    # Notifications
    notification_keywords = ['notification', 'alert', 'reminder', 'update', 
                            'mentioned you', 'commented', 'replied']
    if any(kw in combined for kw in notification_keywords):
        return 'notification'
    
    # Marketing/Promotional
    promo_keywords = ['sale', 'discount', 'offer', 'deal', 'limited time', 
                     'save', 'free shipping', 'promo']
    if any(kw in combined for kw in promo_keywords):
        return 'promotional'
    
    # Conversation (likely personal/work)
    if subject.startswith('re:') or subject.startswith('fwd:'):
        return 'conversation'
    
    return 'other'

def get_message_metadata(service, msg_id):
    """Get message metadata efficiently."""
    try:
        msg = service.users().messages().get(
            userId='me', 
            id=msg_id, 
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date', 'List-Unsubscribe']
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        
        # Parse date
        date_str = headers.get('Date', '')
        try:
            # Simple date parsing - just extract year-month for age analysis
            date_match = re.search(r'\d{1,2}\s+\w+\s+(\d{4})', date_str)
            year = int(date_match.group(1)) if date_match else None
        except:
            year = None
        
        return {
            'id': msg_id,
            'subject': headers.get('Subject', '(no subject)'),
            'from': headers.get('From', ''),
            'date': date_str,
            'year': year,
            'has_unsubscribe': 'List-Unsubscribe' in headers,
            'snippet': msg.get('snippet', '')[:300],
            'internal_date': int(msg.get('internalDate', 0)) // 1000  # Convert to seconds
        }
    except Exception as e:
        print(f"Error getting message {msg_id}: {e}", file=sys.stderr)
        return None

def main():
    start_time = datetime.now()
    print("🔍 Starting Gmail Everything Else audit...", file=sys.stderr)
    
    results = {
        'total_count': 0,
        'sampled_count': 0,
        'top_senders': [],
        'top_domains': [],
        'categories': {},
        'age_distribution': {},
        'cleanup_opportunities': [],
        'oldest_email': None,
        'newest_email': None,
        'median_age_days': None
    }
    
    try:
        creds = get_credentials()
        if not creds:
            results['error'] = 'No valid credentials'
            print(json.dumps(results, indent=2))
            return
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Query for Everything Else category
        # In Gmail, "Everything Else" is basically: not Primary, not Social, not Promotions
        # We'll use: -category:primary -category:social -category:promotions
        query = 'category:updates OR category:forums OR -category:primary -category:social -category:promotions'
        
        print(f"📧 Querying Gmail API...", file=sys.stderr)
        
        # Get total count first
        initial_results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=1
        ).execute()
        
        results['total_count'] = initial_results.get('resultSizeEstimate', 0)
        print(f"📊 Found {results['total_count']} emails in Everything Else category", file=sys.stderr)
        
        # Sample strategy: Get first 500 messages for analysis
        # This gives us a good statistical sample
        all_message_ids = []
        page_token = None
        sample_limit = 500
        
        while len(all_message_ids) < sample_limit:
            try:
                page_results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=min(500, sample_limit - len(all_message_ids)),
                    pageToken=page_token
                ).execute()
                
                messages = page_results.get('messages', [])
                all_message_ids.extend([m['id'] for m in messages])
                
                page_token = page_results.get('nextPageToken')
                if not page_token:
                    break
                    
                print(f"  Collected {len(all_message_ids)} message IDs...", file=sys.stderr)
                
            except Exception as e:
                print(f"Error fetching messages: {e}", file=sys.stderr)
                break
        
        print(f"🔬 Analyzing {len(all_message_ids)} sampled emails...", file=sys.stderr)
        
        # Analyze sampled messages
        sender_counts = Counter()
        domain_counts = Counter()
        category_counts = Counter()
        year_counts = Counter()
        email_ages = []
        
        now_ts = datetime.now().timestamp()
        
        for i, msg_id in enumerate(all_message_ids):
            if i % 50 == 0:
                print(f"  Processed {i}/{len(all_message_ids)}...", file=sys.stderr)
            
            metadata = get_message_metadata(service, msg_id)
            if not metadata:
                continue
            
            # Sender analysis
            sender = extract_sender_name(metadata['from'])
            sender_counts[sender] += 1
            
            # Domain analysis
            domain = extract_domain(sender)
            domain_counts[domain] += 1
            
            # Category analysis
            category = categorize_email_type(
                metadata['subject'],
                metadata['from'],
                metadata['snippet']
            )
            category_counts[category] += 1
            
            # Age analysis
            if metadata['year']:
                year_counts[metadata['year']] += 1
            
            if metadata['internal_date']:
                age_days = (now_ts - metadata['internal_date']) / 86400
                email_ages.append(age_days)
            
            # Track oldest/newest
            if not results['oldest_email'] or (metadata['internal_date'] and 
                metadata['internal_date'] < results.get('oldest_email', {}).get('timestamp', float('inf'))):
                results['oldest_email'] = {
                    'subject': metadata['subject'],
                    'from': metadata['from'],
                    'date': metadata['date'],
                    'timestamp': metadata['internal_date']
                }
            
            if not results['newest_email'] or (metadata['internal_date'] and 
                metadata['internal_date'] > results.get('newest_email', {}).get('timestamp', 0)):
                results['newest_email'] = {
                    'subject': metadata['subject'],
                    'from': metadata['from'],
                    'date': metadata['date'],
                    'timestamp': metadata['internal_date']
                }
        
        results['sampled_count'] = len(all_message_ids)
        
        # Compile results
        results['top_senders'] = [
            {'sender': s, 'count': c, 'estimated_total': int(c * results['total_count'] / results['sampled_count'])}
            for s, c in sender_counts.most_common(15)
        ]
        
        results['top_domains'] = [
            {'domain': d, 'count': c, 'estimated_total': int(c * results['total_count'] / results['sampled_count'])}
            for d, c in domain_counts.most_common(15)
        ]
        
        results['categories'] = {
            cat: {
                'count': count,
                'percentage': round(count / results['sampled_count'] * 100, 1),
                'estimated_total': int(count * results['total_count'] / results['sampled_count'])
            }
            for cat, count in category_counts.items()
        }
        
        results['age_distribution'] = {
            'by_year': dict(sorted(year_counts.items())),
            'oldest_days': int(max(email_ages)) if email_ages else None,
            'newest_days': int(min(email_ages)) if email_ages else None,
            'median_days': int(sorted(email_ages)[len(email_ages)//2]) if email_ages else None,
            'mean_days': int(sum(email_ages) / len(email_ages)) if email_ages else None
        }
        
        # Generate cleanup opportunities
        cleanup_opps = []
        
        # 1. High-volume senders
        for sender_info in results['top_senders'][:5]:
            if sender_info['estimated_total'] > 20:
                cleanup_opps.append({
                    'type': 'bulk_sender',
                    'description': f"Archive all {sender_info['estimated_total']} emails from {sender_info['sender'][:50]}",
                    'query': f'from:{sender_info["sender"][:30]}',
                    'estimated_count': sender_info['estimated_total'],
                    'risk': 'low' if any(kw in sender_info['sender'].lower() for kw in ['noreply', 'notification', 'newsletter']) else 'medium'
                })
        
        # 2. Old emails
        if results['age_distribution']['oldest_days'] > 365:
            years_old = results['age_distribution']['oldest_days'] // 365
            cleanup_opps.append({
                'type': 'age_based',
                'description': f"Archive emails older than {years_old} years",
                'query': f'older_than:{years_old}y',
                'estimated_count': sum(1 for age in email_ages if age > years_old * 365),
                'risk': 'low'
            })
        
        # 3. Category-based
        for cat, info in results['categories'].items():
            if cat in ['newsletter', 'promotional', 'notification'] and info['estimated_total'] > 50:
                cleanup_opps.append({
                    'type': 'category_based',
                    'description': f"Archive all {info['estimated_total']} {cat} emails",
                    'estimated_count': info['estimated_total'],
                    'risk': 'low' if cat in ['newsletter', 'promotional'] else 'medium'
                })
        
        # 4. Domain-based opportunities
        for domain_info in results['top_domains'][:5]:
            domain = domain_info['domain']
            if any(kw in domain.lower() for kw in ['noreply', 'notifications', 'newsletter', 'marketing']):
                cleanup_opps.append({
                    'type': 'domain_based',
                    'description': f"Archive all {domain_info['estimated_total']} emails from {domain}",
                    'query': f'from:@{domain}',
                    'estimated_count': domain_info['estimated_total'],
                    'risk': 'low'
                })
        
        # Sort by estimated count (biggest wins first)
        cleanup_opps.sort(key=lambda x: x['estimated_count'], reverse=True)
        results['cleanup_opportunities'] = cleanup_opps[:10]
        
    except Exception as e:
        results['error'] = str(e)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)
    
    end_time = datetime.now()
    results['timing'] = {
        'start': start_time.isoformat(),
        'end': end_time.isoformat(),
        'duration_seconds': int((end_time - start_time).total_seconds())
    }
    
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
