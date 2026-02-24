#!/usr/bin/env python3
"""
Authentication Token Harvester
Captures auth tokens from browser session for API access
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class AuthTokenHarvester:
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
    
    async def harvest_tokens_interactive(self):
        """Harvest tokens with human assistance for login"""
        print("🎯 Interactive Token Harvesting")
        print("=" * 40)
        print("This method will:")
        print("1. Open a real browser window")
        print("2. Let YOU log in manually (solve CAPTCHAs etc)")  
        print("3. Capture the auth tokens automatically")
        print("4. Save tokens for API usage")
        print()
        input("Press Enter to continue...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Visible browser for human interaction
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                context = await browser.new_context()
                page = await context.new_page()
                
                # Capture all network requests to find auth tokens
                auth_headers = {}
                api_tokens = {}
                
                def capture_request(request):
                    url = request.url
                    headers = dict(request.headers)
                    
                    # Look for auth-related headers
                    auth_keys = ['authorization', 'x-auth-token', 'x-api-key', 'bearer', 'token', 'session-id']
                    for key, value in headers.items():
                        if any(auth_key in key.lower() for auth_key in auth_keys):
                            auth_headers[key] = value
                            print(f"🔑 Found auth header: {key} = {value[:20]}...")
                    
                    # Capture API calls to PCX
                    if 'api.pcexpress.ca' in url:
                        api_tokens[url] = {
                            'headers': headers,
                            'method': request.method,
                            'timestamp': datetime.now().isoformat()
                        }
                        print(f"📡 API Call: {request.method} {url}")
                
                page.on('request', capture_request)
                
                print("🌐 Opening Zehrs sign-in page...")
                await page.goto("https://www.zehrs.ca/en/sign-in")
                
                print("\\n" + "="*50)
                print("👤 MANUAL LOGIN REQUIRED")
                print("="*50)
                print("Please:")
                print("1. Log in with your credentials")
                print("2. Solve any CAPTCHAs")
                print("3. Navigate to your cart or account page")
                print("4. Press Enter here when done")
                print("="*50)
                
                input("Press Enter after you've logged in and visited your cart/account...")
                
                # Force some API calls to capture tokens
                print("🔄 Triggering API calls to capture tokens...")
                
                try:
                    # Visit cart to trigger API calls
                    await page.goto("https://www.zehrs.ca/en/cart", wait_until='networkidle')
                    await page.wait_for_timeout(3000)
                    
                    # Visit account/profile
                    await page.goto("https://www.zehrs.ca/en/my-account", wait_until='networkidle') 
                    await page.wait_for_timeout(3000)
                    
                    # Visit deals page
                    await page.goto("https://www.zehrs.ca/en/deals-and-flyer", wait_until='networkidle')
                    await page.wait_for_timeout(3000)
                    
                except Exception as nav_error:
                    print(f"⚠️ Navigation warning: {nav_error}")
                
                # Get final cookies as backup auth method
                cookies = await context.cookies()
                auth_cookies = {cookie['name']: cookie['value'] for cookie in cookies 
                              if any(auth_term in cookie['name'].lower() 
                                   for auth_term in ['auth', 'session', 'token', 'jwt', 'bearer'])}
                
                # Save all captured auth data
                auth_data = {
                    'captured_at': datetime.now().isoformat(),
                    'headers': auth_headers,
                    'api_calls': api_tokens,
                    'auth_cookies': auth_cookies,
                    'all_cookies': [{'name': c['name'], 'value': c['value'], 'domain': c['domain']} 
                                  for c in cookies]
                }
                
                with open(self.token_file, 'w') as f:
                    json.dump(auth_data, f, indent=2)
                
                print(f"\\n💾 Auth data saved to: {self.token_file}")
                print(f"🔑 Auth headers found: {len(auth_headers)}")
                print(f"📡 API calls captured: {len(api_tokens)}")
                print(f"🍪 Auth cookies found: {len(auth_cookies)}")
                
                return auth_data
                
            finally:
                print("\\nClosing browser in 5 seconds...")
                await asyncio.sleep(5)
                await browser.close()
    
    async def test_harvested_tokens(self):
        """Test the harvested tokens against the API"""
        if not os.path.exists(self.token_file):
            print("❌ No tokens file found. Run harvest first.")
            return False
        
        print("🧪 Testing harvested authentication tokens...")
        
        with open(self.token_file, 'r') as f:
            auth_data = json.load(f)
        
        # Build headers from captured data
        test_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': 'https://www.zehrs.ca/',
            'site-banner': 'zehrs',
            'basesiteid': 'zehrs',
            'x-channel': 'web'
        }
        
        # Add captured auth headers
        test_headers.update(auth_data.get('headers', {}))
        
        # Test with aiohttp
        import aiohttp
        
        test_endpoints = [
            '/cart',
            '/user/profile', 
            '/products/featured',
            '/deals'
        ]
        
        async with aiohttp.ClientSession() as session:
            success_count = 0
            
            for endpoint in test_endpoints:
                url = f"https://api.pcexpress.ca/pcx-bff/api/v1{endpoint}"
                
                try:
                    async with session.get(url, headers=test_headers) as response:
                        status = response.status
                        
                        if status == 200:
                            print(f"✅ {endpoint} - SUCCESS!")
                            success_count += 1
                            
                            # Save successful response
                            try:
                                data = await response.json()
                                filename = f"/home/magi/clawd/grocery-data/api_success_{endpoint.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                with open(filename, 'w') as f:
                                    json.dump(data, f, indent=2)
                                print(f"   💾 Response saved: {filename}")
                            except:
                                pass
                                
                        elif status == 401:
                            print(f"❌ {endpoint} - Still unauthorized")
                        else:
                            print(f"⚠️ {endpoint} - Status {status}")
                            
                except Exception as e:
                    print(f"❌ {endpoint} - Error: {e}")
                
                await asyncio.sleep(1)
            
            if success_count > 0:
                print(f"\\n🎉 SUCCESS! {success_count}/{len(test_endpoints)} endpoints working!")
                print("🚀 You now have direct API access to Zehrs data!")
                return True
            else:
                print(f"\\n❌ No endpoints working yet. May need different auth approach.")
                return False

async def main():
    harvester = AuthTokenHarvester()
    
    print("🎯 ZEHRS API TOKEN HARVESTER")
    print("=" * 40)
    print("Choose an option:")
    print("1. Harvest tokens (interactive login)")
    print("2. Test existing tokens")
    print("3. Both (harvest then test)")
    
    choice = input("\\nEnter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        auth_data = await harvester.harvest_tokens_interactive()
        if auth_data:
            print("\\n✅ Token harvesting complete!")
        else:
            print("\\n❌ Token harvesting failed")
            return
    
    if choice in ['2', '3']:
        success = await harvester.test_harvested_tokens()
        if success:
            print("\\n🎉 API ACCESS ACHIEVED!")
            print("\\nYou can now:")
            print("- Access your cart programmatically") 
            print("- Get purchase history")
            print("- Manage favorites")
            print("- Track deals and promotions")
        else:
            print("\\n🔄 API access not yet working")

if __name__ == "__main__":
    asyncio.run(main())