#!/usr/bin/env python3
"""
HAR Cookie Extractor - Extract ALL cookies from HAR file
"""

import json

def extract_all_cookies():
    """Extract all cookies from HAR file"""
    har_file = '/mnt/bigstore/knowledge/shared/transfers/www.zehrs.ca.har'
    
    print("🍪 COMPREHENSIVE COOKIE EXTRACTION")
    print("=" * 40)
    
    with open(har_file, 'r') as f:
        har_data = json.load(f)
    
    entries = har_data.get('log', {}).get('entries', [])
    all_cookies = {}
    cookie_sources = {}
    
    for entry in entries:
        url = entry.get('request', {}).get('url', '')
        
        # Extract request cookies
        request_cookies = entry.get('request', {}).get('cookies', [])
        for cookie in request_cookies:
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            if name and value:
                all_cookies[name] = value
                cookie_sources[name] = f"Request to {url}"
        
        # Extract response cookies (Set-Cookie headers)
        response_cookies = entry.get('response', {}).get('cookies', [])
        for cookie in response_cookies:
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            if name and value:
                all_cookies[name] = value
                cookie_sources[name] = f"Response from {url}"
    
    print(f"📊 Total unique cookies found: {len(all_cookies)}")
    print()
    
    # Group cookies by likely importance
    auth_cookies = {}
    session_cookies = {}
    tracking_cookies = {}
    other_cookies = {}
    
    for name, value in all_cookies.items():
        name_lower = name.lower()
        
        # Authentication-related
        if any(term in name_lower for term in ['auth', 'token', 'jwt', 'bearer', 'login', 'user', 'account', 'session', 'sid']):
            auth_cookies[name] = value
        # Session-related
        elif any(term in name_lower for term in ['sess', 'jsession', 'phpsess', 'asp.net', 'connect.sid']):
            session_cookies[name] = value
        # Tracking/Analytics
        elif any(term in name_lower for term in ['_ga', '_gid', '_gat', '_gtm', 'utm', 'fbp', '_fbp', 'tr', 'pixel']):
            tracking_cookies[name] = value
        # Everything else
        else:
            other_cookies[name] = value
    
    print("🔑 AUTHENTICATION/SESSION COOKIES:")
    for name, value in auth_cookies.items():
        print(f"  {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
        print(f"    Source: {cookie_sources.get(name, 'Unknown')}")
        print()
    
    print("🍪 OTHER SESSION COOKIES:")
    for name, value in session_cookies.items():
        print(f"  {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
        print(f"    Source: {cookie_sources.get(name, 'Unknown')}")
        print()
    
    print("📊 OTHER POTENTIALLY USEFUL COOKIES:")
    interesting_other = {k: v for k, v in other_cookies.items() 
                        if len(v) > 20 or any(term in k.lower() for term in 
                             ['pcx', 'express', 'zehrs', 'loblaws', 'cart', 'customer'])}
    
    for name, value in interesting_other.items():
        print(f"  {name}: {value[:50]}{'...' if len(value) > 50 else ''}")
        print(f"    Source: {cookie_sources.get(name, 'Unknown')}")
        print()
    
    # Create combined cookie header
    all_auth_cookies = {**auth_cookies, **session_cookies, **interesting_other}
    
    if all_auth_cookies:
        cookie_header = '; '.join([f"{name}={value}" for name, value in all_auth_cookies.items()])
        
        print("🎯 COMPLETE COOKIE HEADER FOR API:")
        print(f"Cookie: {cookie_header}")
        print()
        
        # Save to file
        cookie_data = {
            'auth_cookies': auth_cookies,
            'session_cookies': session_cookies, 
            'interesting_cookies': interesting_other,
            'cookie_header': cookie_header,
            'all_cookies': all_cookies
        }
        
        with open('/home/magi/clawd/grocery-data/extracted_cookies.json', 'w') as f:
            json.dump(cookie_data, f, indent=2)
        
        print("💾 All cookies saved to: /home/magi/clawd/grocery-data/extracted_cookies.json")
        return cookie_header
    else:
        print("❌ No authentication cookies found")
        return None

if __name__ == "__main__":
    extract_all_cookies()