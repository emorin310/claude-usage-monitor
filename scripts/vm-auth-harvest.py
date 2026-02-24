#!/usr/bin/env python3
"""
VM Authentication Harvest - Optimized for this environment
Uses the working stealth techniques we just discovered
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class VMAuthHarvest:
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
    
    async def vm_optimized_harvest(self):
        """Optimized harvest using techniques that work on this VM"""
        print("🖥️ VM-OPTIMIZED AUTHENTICATION HARVEST")
        print("=" * 45)
        print("Using proven working techniques from diagnostic")
        print()
        
        async with async_playwright() as p:
            try:
                # Use the working configuration from diagnostic
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--exclude-switches=enable-automation',
                        '--disable-extensions'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                
                page = await context.new_page()
                page.set_default_timeout(30000)  # 30 seconds - we know it works
                
                # Capture network requests for API tokens
                captured_data = {
                    'headers': {},
                    'api_calls': {},
                    'cookies': []
                }
                
                def capture_request(request):
                    url = request.url
                    headers = dict(request.headers)
                    
                    # Look for auth tokens in headers
                    auth_keys = ['authorization', 'x-auth-token', 'bearer', 'session-id', 'x-api-key', 'access-token']
                    for key, value in headers.items():
                        if any(auth_key in key.lower() for auth_key in auth_keys):
                            captured_data['headers'][key] = value
                            print(f"🔑 Auth header found: {key}")
                    
                    # Capture PC Express API calls
                    if 'api.pcexpress.ca' in url or 'pcx-bff' in url:
                        captured_data['api_calls'][url] = {
                            'method': request.method,
                            'headers': headers,
                            'timestamp': datetime.now().isoformat()
                        }
                        print(f"📡 API call captured: {request.method} {url}")
                
                page.on('request', capture_request)
                
                print("🌐 Step 1: Loading Zehrs homepage...")
                await page.goto('https://www.zehrs.ca/en', wait_until='networkidle')
                await page.wait_for_timeout(2000)
                
                print("🔐 Step 2: Navigating to sign-in...")
                await page.goto('https://www.zehrs.ca/en/sign-in', wait_until='networkidle')
                await page.wait_for_timeout(3000)
                
                print("📝 Step 3: Attempting automated login...")
                try:
                    # Look for email field with multiple selectors
                    email_selectors = [
                        'input[type="email"]',
                        'input[name="email"]', 
                        '#email',
                        '[data-testid="email"]',
                        'input[placeholder*="email" i]'
                    ]
                    
                    email_filled = False
                    for selector in email_selectors:
                        try:
                            await page.wait_for_selector(selector, timeout=5000)
                            await page.fill(selector, self.email)
                            print(f"✅ Email filled with selector: {selector}")
                            email_filled = True
                            break
                        except:
                            continue
                    
                    if not email_filled:
                        print("❌ Could not find email field")
                        return False
                    
                    # Look for password field
                    password_selectors = [
                        'input[type="password"]',
                        'input[name="password"]',
                        '#password',
                        '[data-testid="password"]'
                    ]
                    
                    password_filled = False
                    for selector in password_selectors:
                        try:
                            await page.wait_for_selector(selector, timeout=5000)
                            await page.fill(selector, self.password)
                            print(f"✅ Password filled with selector: {selector}")
                            password_filled = True
                            break
                        except:
                            continue
                    
                    if not password_filled:
                        print("❌ Could not find password field")
                        return False
                    
                    print("⏳ Waiting 2 seconds before submit...")
                    await page.wait_for_timeout(2000)
                    
                    # Submit the form
                    submit_selectors = [
                        'button[type="submit"]',
                        'input[type="submit"]', 
                        'button:has-text("Sign In")',
                        'button:has-text("Log In")',
                        '[data-testid="submit"]'
                    ]
                    
                    submitted = False
                    for selector in submit_selectors:
                        try:
                            await page.click(selector)
                            print(f"✅ Submit clicked: {selector}")
                            submitted = True
                            break
                        except:
                            continue
                    
                    if not submitted:
                        print("⌨️ Trying Enter key...")
                        await page.keyboard.press('Enter')
                    
                    print("⏳ Waiting for login response...")
                    await page.wait_for_timeout(8000)
                    
                    # Check login result
                    current_url = page.url
                    title = await page.title()
                    
                    print(f"📍 After login - URL: {current_url}")
                    print(f"📄 Title: {title}")
                    
                    # Test accessing protected areas
                    protected_urls = [
                        'https://www.zehrs.ca/en/my-account',
                        'https://www.zehrs.ca/en/cart'
                    ]
                    
                    for test_url in protected_urls:
                        try:
                            print(f"🔍 Testing access to: {test_url}")
                            await page.goto(test_url, wait_until='networkidle')
                            await page.wait_for_timeout(3000)
                            
                            test_title = await page.title()
                            if 'sign-in' not in page.url and 'login' not in page.url:
                                print(f"✅ Access granted to: {test_title}")
                            else:
                                print(f"❌ Redirected to login for: {test_url}")
                                
                        except Exception as nav_error:
                            print(f"⚠️ Navigation issue: {nav_error}")
                    
                    # Get all cookies
                    cookies = await context.cookies()
                    captured_data['cookies'] = cookies
                    
                    # Filter for auth cookies
                    auth_cookies = {c['name']: c['value'] for c in cookies 
                                  if any(term in c['name'].lower() for term in 
                                       ['auth', 'session', 'token', 'jwt', 'access', 'refresh'])}
                    
                    print(f"🍪 Found {len(auth_cookies)} potential auth cookies")
                    for cookie_name in list(auth_cookies.keys())[:3]:
                        print(f"   • {cookie_name}")
                    
                    # Save captured data
                    auth_data = {
                        'method': 'vm_optimized_harvest',
                        'captured_at': datetime.now().isoformat(),
                        'login_success': 'sign-in' not in current_url,
                        'auth_headers': captured_data['headers'],
                        'api_calls': captured_data['api_calls'],
                        'auth_cookies': auth_cookies,
                        'all_cookies': [{'name': c['name'], 'value': c['value'], 'domain': c['domain']} 
                                      for c in cookies],
                        'final_url': current_url,
                        'final_title': title
                    }
                    
                    with open(self.token_file, 'w') as f:
                        json.dump(auth_data, f, indent=2)
                    
                    print(f"\n💾 Auth data saved to: {self.token_file}")
                    print(f"🔑 Auth headers: {len(captured_data['headers'])}")
                    print(f"📡 API calls: {len(captured_data['api_calls'])}")
                    print(f"🍪 Auth cookies: {len(auth_cookies)}")
                    
                    return len(captured_data['headers']) > 0 or len(auth_cookies) > 0
                    
                except Exception as login_error:
                    print(f"❌ Login process error: {login_error}")
                    return False
                
            finally:
                await browser.close()
    
    async def test_captured_auth(self):
        """Test the captured authentication data"""
        if not os.path.exists(self.token_file):
            print("❌ No auth data file found")
            return False
        
        print("\n🧪 TESTING CAPTURED AUTHENTICATION")
        print("-" * 35)
        
        with open(self.token_file, 'r') as f:
            auth_data = json.load(f)
        
        # Build headers for API testing
        test_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': 'https://www.zehrs.ca/',
            'site-banner': 'zehrs',
            'basesiteid': 'zehrs',
            'x-channel': 'web'
        }
        
        # Add captured auth headers
        test_headers.update(auth_data.get('auth_headers', {}))
        
        import aiohttp
        
        test_endpoints = [
            ('/cart', 'Shopping Cart'),
            ('/user/profile', 'User Profile'),
            ('/deals', 'Current Deals'),
            ('/user/orders', 'Order History')
        ]
        
        successes = 0
        
        async with aiohttp.ClientSession() as session:
            for endpoint, description in test_endpoints:
                url = f"https://api.pcexpress.ca/pcx-bff/api/v1{endpoint}"
                
                try:
                    async with session.get(url, headers=test_headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        status = response.status
                        
                        if status == 200:
                            print(f"✅ {description}: SUCCESS! (200)")
                            successes += 1
                            
                            # Try to get sample data
                            try:
                                data = await response.json()
                                print(f"   📊 Response data: {len(str(data))} characters")
                                
                                # Save successful response
                                response_file = f"/home/magi/clawd/grocery-data/api_success_{endpoint.replace('/', '_')}.json"
                                with open(response_file, 'w') as f:
                                    json.dump(data, f, indent=2)
                                print(f"   💾 Data saved: {response_file}")
                                
                            except Exception as json_error:
                                text = await response.text()
                                print(f"   📝 Response text: {text[:100]}...")
                        
                        elif status == 401:
                            print(f"❌ {description}: Unauthorized (401)")
                        elif status == 403:
                            print(f"❌ {description}: Forbidden (403)")
                        else:
                            print(f"⚠️ {description}: Status {status}")
                
                except Exception as test_error:
                    print(f"❌ {description}: Error - {test_error}")
                
                await asyncio.sleep(1)
        
        print(f"\n📊 API Test Results: {successes}/{len(test_endpoints)} endpoints working")
        
        if successes > 0:
            print("🎉 AUTHENTICATION SUCCESS!")
            print("✅ You now have working API access to Zehrs!")
            return True
        else:
            print("🔄 Authentication data captured but API access not yet working")
            print("💡 May need different approach or additional steps")
            return False

async def main():
    harvester = VMAuthHarvest()
    
    if not harvester.email or not harvester.password:
        print("❌ No Zehrs credentials found")
        return
    
    print(f"🔐 Using credentials: {harvester.email}")
    print()
    
    # Run the harvest
    harvest_success = await harvester.vm_optimized_harvest()
    
    if harvest_success:
        print("\n✅ Authentication data captured!")
        
        # Test the captured data
        api_success = await harvester.test_captured_auth()
        
        if api_success:
            print("\n🎉 COMPLETE SUCCESS!")
            print("🛒 Full grocery automation is now available!")
            print("📊 You can access cart, orders, deals, and profile data")
        else:
            print("\n🔄 Partial success - auth data captured")
            print("💡 May need refinement for full API access")
    else:
        print("\n❌ Authentication harvest failed")
        print("🔄 May need different approach")

if __name__ == "__main__":
    asyncio.run(main())