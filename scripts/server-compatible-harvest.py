#!/usr/bin/env python3
"""
Server-Compatible Token Harvest  
Alternative approach that works in headless server environments
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class ServerCompatibleHarvest:
    def __init__(self):
        self.email, self.password = self.load_credentials()
        self.token_file = "/home/magi/clawd/grocery-data/api_tokens.json"
        
    def load_credentials(self):
        """Load Zehrs credentials"""
        secrets_path = "/mnt/bigstore/knowledge/shared/secrets.env"
        email = password = None
        
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key == 'ZEHRS_EMAIL':
                            email = value
                        elif key == 'ZEHRS_PASSWORD':
                            password = value
        return email, password
    
    async def method_session_inspection(self):
        """Inspect existing browser sessions for tokens"""
        print("🔍 Method 1: Session Inspection...")
        
        # Check for existing browser session files
        browser_dirs = [
            "/home/magi/.config/chromium",
            "/home/magi/.config/google-chrome", 
            "/tmp/playwright*",
            "/home/magi/.cache/ms-playwright"
        ]
        
        for browser_dir in browser_dirs:
            if os.path.exists(browser_dir):
                print(f"✅ Found browser cache: {browser_dir}")
                # Could extract session data here
            else:
                print(f"❌ No cache found: {browser_dir}")
        
        return False
    
    async def method_stealth_headless(self):
        """Try stealth login in headless mode"""
        print("🕵️ Method 2: Stealth Headless Login...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,  # Must be headless for server
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                ]
            )
            
            try:
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                
                page = await context.new_page()
                
                # Capture network requests
                captured_headers = {}
                
                def capture_request(request):
                    url = request.url
                    headers = dict(request.headers)
                    
                    # Look for auth-related requests
                    if 'api.pcexpress.ca' in url or 'zehrs.ca' in url:
                        auth_keys = ['authorization', 'x-auth-token', 'bearer', 'session-id', 'x-api-key']
                        for key, value in headers.items():
                            if any(auth_key in key.lower() for auth_key in auth_keys):
                                captured_headers[key] = value
                                print(f"🔑 Captured: {key} = {value[:20]}...")
                
                page.on('request', capture_request)
                
                print("🌐 Attempting headless login...")
                await page.goto("https://www.zehrs.ca/en/sign-in", wait_until='networkidle')
                
                # Try automated form filling
                try:
                    # Wait for email field
                    await page.wait_for_selector('input[type="email"]', timeout=10000)
                    await page.fill('input[type="email"]', self.email)
                    
                    # Wait for password field
                    await page.wait_for_selector('input[type="password"]', timeout=5000)
                    await page.fill('input[type="password"]', self.password)
                    
                    # Submit form
                    await page.click('button[type="submit"]')
                    
                    # Wait for response
                    await page.wait_for_timeout(5000)
                    
                    # Check if login worked
                    current_url = page.url
                    title = await page.title()
                    
                    print(f"📍 After login - URL: {current_url}")
                    print(f"📄 Title: {title}")
                    
                    # Try to access protected areas to trigger API calls
                    test_urls = [
                        "https://www.zehrs.ca/en/my-account",
                        "https://www.zehrs.ca/en/cart",
                        "https://www.zehrs.ca/en/deals-and-flyer"
                    ]
                    
                    for test_url in test_urls:
                        try:
                            print(f"🔍 Testing: {test_url}")
                            await page.goto(test_url, wait_until='networkidle')
                            await page.wait_for_timeout(3000)
                        except Exception as nav_error:
                            print(f"⚠️ Navigation issue: {nav_error}")
                    
                    # Get cookies as backup
                    cookies = await context.cookies()
                    auth_cookies = {c['name']: c['value'] for c in cookies 
                                  if any(auth_term in c['name'].lower() 
                                       for auth_term in ['auth', 'session', 'token', 'jwt'])}
                    
                    if captured_headers or auth_cookies:
                        auth_data = {
                            'method': 'stealth_headless',
                            'captured_at': datetime.now().isoformat(),
                            'headers': captured_headers,
                            'auth_cookies': auth_cookies,
                            'all_cookies': [{'name': c['name'], 'value': c['value']} for c in cookies]
                        }
                        
                        with open(self.token_file, 'w') as f:
                            json.dump(auth_data, f, indent=2)
                        
                        print(f"💾 Auth data saved: {len(captured_headers)} headers, {len(auth_cookies)} auth cookies")
                        return True
                    else:
                        print("❌ No authentication data captured")
                        return False
                        
                except Exception as login_error:
                    print(f"❌ Login error: {login_error}")
                    return False
                    
            finally:
                await browser.close()
    
    async def method_api_reverse_engineering(self):
        """Try to reverse engineer the API authentication"""
        print("🔬 Method 3: API Reverse Engineering...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            
            try:
                page = await browser.new_page()
                
                # Monitor all network traffic
                all_requests = []
                
                def log_request(request):
                    all_requests.append({
                        'url': request.url,
                        'method': request.method,
                        'headers': dict(request.headers),
                        'timestamp': datetime.now().isoformat()
                    })
                
                page.on('request', log_request)
                
                print("🌐 Loading Zehrs homepage to analyze requests...")
                await page.goto("https://www.zehrs.ca/en", wait_until='networkidle')
                await page.wait_for_timeout(5000)
                
                # Filter for interesting requests
                api_requests = [req for req in all_requests if 
                              'api.' in req['url'] or 'auth' in req['url'] or 
                              'login' in req['url'] or 'session' in req['url']]
                
                if api_requests:
                    print(f"🎯 Found {len(api_requests)} API-related requests:")
                    for req in api_requests[:5]:
                        print(f"  {req['method']} {req['url']}")
                    
                    # Save analysis
                    analysis_file = "/home/magi/clawd/grocery-data/api_analysis.json"
                    with open(analysis_file, 'w') as f:
                        json.dump(all_requests, f, indent=2)
                    
                    print(f"💾 Full analysis saved: {analysis_file}")
                    return api_requests
                else:
                    print("❌ No API requests found")
                    return []
                    
            finally:
                await browser.close()
    
    async def run_server_compatible_harvest(self):
        """Run all server-compatible methods"""
        print("🖥️ SERVER-COMPATIBLE TOKEN HARVEST")
        print("=" * 45)
        print("🎯 Designed for headless server environments")
        print("⚡ No GUI browser required")
        print()
        
        methods = [
            ("Session Inspection", self.method_session_inspection),
            ("Stealth Headless", self.method_stealth_headless),
            ("API Reverse Engineering", self.method_api_reverse_engineering),
        ]
        
        results = {}
        
        for method_name, method_func in methods:
            print(f"\\n🔄 Trying: {method_name}")
            print("-" * 30)
            
            try:
                result = await method_func()
                results[method_name] = result
                
                if result:
                    print(f"✅ {method_name} successful!")
                else:
                    print(f"❌ {method_name} failed")
                    
            except Exception as e:
                print(f"❌ {method_name} error: {e}")
                results[method_name] = False
            
            await asyncio.sleep(2)
        
        # Summary
        print("\\n" + "=" * 45)
        print("📊 HARVEST RESULTS")
        print("=" * 45)
        
        successes = [name for name, result in results.items() if result]
        
        if successes:
            print(f"✅ Successful methods: {', '.join(successes)}")
            
            # Check for output files
            if os.path.exists(self.token_file):
                print(f"💾 Token file created: {self.token_file}")
                
                # Test the tokens
                print("\\n🧪 Testing captured tokens...")
                await self.test_captured_tokens()
            
            return True
        else:
            print("❌ All methods failed")
            print("\\n💡 Alternative approaches:")
            print("1. Manual session export from your local browser")
            print("2. Browser extension development") 
            print("3. Email receipt parsing for purchase history")
            print("4. Public API endpoints (deals, store locations)")
            
            return False
    
    async def test_captured_tokens(self):
        """Test any captured authentication tokens"""
        if not os.path.exists(self.token_file):
            print("❌ No token file to test")
            return
        
        try:
            with open(self.token_file, 'r') as f:
                auth_data = json.load(f)
            
            print(f"🔍 Testing tokens from: {auth_data.get('method', 'unknown')}")
            
            # Try a simple API call with captured auth
            import aiohttp
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'site-banner': 'zehrs',
                'basesiteid': 'zehrs',
                'x-channel': 'web'
            }
            
            # Add captured headers
            headers.update(auth_data.get('headers', {}))
            
            async with aiohttp.ClientSession() as session:
                test_url = "https://api.pcexpress.ca/pcx-bff/api/v1/cart"
                
                try:
                    async with session.get(test_url, headers=headers) as response:
                        print(f"🧪 Cart API test: {response.status}")
                        
                        if response.status == 200:
                            print("🎉 SUCCESS! API access working!")
                            data = await response.json()
                            print(f"📦 Cart data: {len(str(data))} chars")
                            return True
                        elif response.status == 401:
                            print("❌ Still unauthorized - need better tokens")
                        else:
                            print(f"⚠️ Unexpected status: {response.status}")
                        
                except Exception as test_error:
                    print(f"❌ Test error: {test_error}")
            
        except Exception as e:
            print(f"❌ Token test error: {e}")
        
        return False

async def main():
    harvester = ServerCompatibleHarvest()
    
    if not harvester.email or not harvester.password:
        print("❌ No Zehrs credentials found")
        return
    
    success = await harvester.run_server_compatible_harvest()
    
    if success:
        print("\\n🚀 SUCCESS! Ready for grocery automation!")
    else:
        print("\\n🔄 Consider alternative approaches")

if __name__ == "__main__":
    asyncio.run(main())