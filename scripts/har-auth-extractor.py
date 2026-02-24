#!/usr/bin/env python3
"""
HAR Authentication Extractor
Parses HAR file to extract Zehrs authentication tokens
"""

import json
import sys
from datetime import datetime

class HARAuthExtractor:
    def __init__(self, har_file_path):
        self.har_file = har_file_path
        self.auth_data = {
            'captured_at': datetime.now().isoformat(),
            'method': 'har_file_extraction',
            'auth_headers': {},
            'auth_cookies': {},
            'api_endpoints': [],
            'session_tokens': {}
        }
    
    def extract_auth_data(self):
        """Extract all authentication data from HAR file"""
        print(f"🔍 Analyzing HAR file: {self.har_file}")
        
        try:
            with open(self.har_file, 'r') as f:
                har_data = json.load(f)
            
            entries = har_data.get('log', {}).get('entries', [])
            print(f"📊 Found {len(entries)} network requests")
            
            pcexpress_requests = []
            zehrs_requests = []
            
            for entry in entries:
                url = entry.get('request', {}).get('url', '')
                
                # Filter PC Express API calls
                if 'api.pcexpress.ca' in url:
                    pcexpress_requests.append(entry)
                
                # Filter Zehrs requests
                if 'zehrs.ca' in url:
                    zehrs_requests.append(entry)
            
            print(f"🎯 Found {len(pcexpress_requests)} PC Express API requests")
            print(f"🛒 Found {len(zehrs_requests)} Zehrs requests")
            
            # Extract auth data from API requests
            self.extract_from_api_requests(pcexpress_requests)
            
            # Extract cookies from all requests
            self.extract_cookies(zehrs_requests + pcexpress_requests)
            
            # Save extracted data
            self.save_auth_data()
            
            return self.auth_data
            
        except Exception as e:
            print(f"❌ Error parsing HAR file: {e}")
            return None
    
    def extract_from_api_requests(self, api_requests):
        """Extract authentication headers from API requests"""
        print("\n🔑 Extracting authentication headers...")
        
        for entry in api_requests[:5]:  # Check first 5 API requests
            request = entry.get('request', {})
            url = request.get('url', '')
            method = request.get('method', '')
            headers = request.get('headers', [])
            
            print(f"  📡 {method} {url}")
            
            # Convert headers list to dict
            header_dict = {}
            for header in headers:
                name = header.get('name', '').lower()
                value = header.get('value', '')
                header_dict[name] = value
                
                # Look for auth-related headers
                if any(auth_term in name for auth_term in [
                    'authorization', 'x-auth', 'bearer', 'session', 'token', 'api-key'
                ]):
                    self.auth_data['auth_headers'][header.get('name')] = value
                    print(f"    🔑 Found auth header: {header.get('name')}")
            
            # Store endpoint info
            self.auth_data['api_endpoints'].append({
                'url': url,
                'method': method,
                'status': entry.get('response', {}).get('status', 0),
                'headers': header_dict
            })
    
    def extract_cookies(self, requests):
        """Extract authentication cookies"""
        print("\n🍪 Extracting authentication cookies...")
        
        all_cookies = {}
        
        for entry in requests:
            # Request cookies
            request_cookies = entry.get('request', {}).get('cookies', [])
            for cookie in request_cookies:
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                all_cookies[name] = value
            
            # Response cookies
            response_cookies = entry.get('response', {}).get('cookies', [])
            for cookie in response_cookies:
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                all_cookies[name] = value
        
        # Filter for auth-related cookies
        auth_cookie_terms = [
            'auth', 'session', 'token', 'jwt', 'bearer', 'access', 
            'refresh', 'login', 'user', 'account', 'pcx', 'express'
        ]
        
        for name, value in all_cookies.items():
            name_lower = name.lower()
            if any(term in name_lower for term in auth_cookie_terms):
                self.auth_data['auth_cookies'][name] = value
                print(f"  🔑 Found auth cookie: {name}")
            elif len(value) > 50:  # Long values might be tokens
                self.auth_data['session_tokens'][name] = value
                print(f"  🎫 Found potential token: {name} (length: {len(value)})")
    
    def save_auth_data(self):
        """Save extracted authentication data"""
        output_file = '/home/magi/clawd/grocery-data/extracted_auth_tokens.json'
        
        with open(output_file, 'w') as f:
            json.dump(self.auth_data, f, indent=2)
        
        print(f"\n💾 Authentication data saved to: {output_file}")
        
        # Create API-ready headers
        api_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': 'https://www.zehrs.ca/',
            'site-banner': 'zehrs',
            'basesiteid': 'zehrs',
            'x-channel': 'web'
        }
        
        # Add extracted auth headers
        api_headers.update(self.auth_data['auth_headers'])
        
        # Add cookie header if we have auth cookies
        if self.auth_data['auth_cookies']:
            cookie_string = '; '.join([f"{name}={value}" for name, value in self.auth_data['auth_cookies'].items()])
            api_headers['Cookie'] = cookie_string
        
        # Save API-ready headers
        api_headers_file = '/home/magi/clawd/grocery-data/api_headers.json'
        with open(api_headers_file, 'w') as f:
            json.dump(api_headers, f, indent=2)
        
        print(f"🔧 API-ready headers saved to: {api_headers_file}")
    
    def print_summary(self):
        """Print summary of extracted data"""
        print("\n📊 AUTHENTICATION EXTRACTION SUMMARY")
        print("=" * 45)
        print(f"🔑 Auth Headers Found: {len(self.auth_data['auth_headers'])}")
        print(f"🍪 Auth Cookies Found: {len(self.auth_data['auth_cookies'])}")
        print(f"🎫 Session Tokens Found: {len(self.auth_data['session_tokens'])}")
        print(f"📡 API Endpoints Found: {len(self.auth_data['api_endpoints'])}")
        
        if self.auth_data['auth_headers']:
            print("\n🔑 Authentication Headers:")
            for name, value in self.auth_data['auth_headers'].items():
                print(f"  • {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
        
        if self.auth_data['auth_cookies']:
            print("\n🍪 Authentication Cookies:")
            for name, value in self.auth_data['auth_cookies'].items():
                print(f"  • {name}: {value[:50]}{'...' if len(value) > 50 else ''}")

def main():
    har_file = '/mnt/bigstore/knowledge/shared/transfers/www.zehrs.ca.har'
    
    extractor = HARAuthExtractor(har_file)
    auth_data = extractor.extract_auth_data()
    
    if auth_data:
        extractor.print_summary()
        print("\n🎯 NEXT STEP: Test cart editing with extracted tokens!")
        print("Run: python scripts/cart-manager.py")
    else:
        print("❌ Failed to extract authentication data")

if __name__ == "__main__":
    main()