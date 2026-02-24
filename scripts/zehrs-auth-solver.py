#!/usr/bin/env python3
"""
Zehrs Authentication Solver - Advanced Multi-Method Approach
Attempts multiple techniques to solve Zehrs.ca login automation
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

class ZehrsAuthSolver:
    def __init__(self):
        self.email, self.password = self.load_credentials()
        self.session_file = "/home/magi/clawd/grocery-data/zehrs_session.json"
        
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
    
    async def method_1_stealth_login(self):
        """Method 1: Stealth browser with anti-detection"""
        print("🕵️ Attempting Method 1: Stealth Login...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Try visible browser first
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            try:
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                
                page = await context.new_page()
                
                # Add stealth scripts
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = {runtime: {}};
                """)
                
                print("🌐 Navigating to Zehrs sign-in...")
                await page.goto("https://www.zehrs.ca/en/sign-in", wait_until='networkidle')
                
                # Wait for human to solve CAPTCHA if needed
                print("⏳ Waiting 10 seconds for page to fully load (and CAPTCHA if present)...")
                await page.wait_for_timeout(10000)
                
                # Try multiple login strategies
                login_success = await self.attempt_login_forms(page)
                
                if login_success:
                    # Test cart access
                    await page.goto("https://www.zehrs.ca/en/cart", wait_until='networkidle')
                    title = await page.title()
                    
                    if "cart" in title.lower() and "404" not in title:
                        print("✅ Method 1 successful - cart accessible!")
                        
                        # Save session cookies
                        cookies = await context.cookies()
                        with open(self.session_file, 'w') as f:
                            json.dump({
                                'method': 'stealth_login',
                                'cookies': cookies,
                                'timestamp': datetime.now().isoformat()
                            }, f, indent=2)
                        
                        return True
                
                return False
                
            except Exception as e:
                print(f"❌ Method 1 error: {e}")
                return False
            finally:
                await browser.close()
    
    async def method_2_session_persistence(self):
        """Method 2: Load existing session if available"""
        print("💾 Attempting Method 2: Session Persistence...")
        
        if not os.path.exists(self.session_file):
            print("❌ No saved session found")
            return False
        
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is recent (within 24 hours)
            session_time = datetime.fromisoformat(session_data['timestamp'])
            if (datetime.now() - session_time).total_seconds() > 86400:  # 24 hours
                print("⏰ Saved session too old")
                return False
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
                context = await browser.new_context()
                
                # Restore cookies
                await context.add_cookies(session_data['cookies'])
                
                page = await context.new_page()
                await page.goto("https://www.zehrs.ca/en/cart", wait_until='networkidle')
                
                title = await page.title()
                if "cart" in title.lower() and "404" not in title and "sign-in" not in page.url:
                    print("✅ Method 2 successful - session restored!")
                    return True
                else:
                    print("❌ Saved session expired or invalid")
                    return False
                    
        except Exception as e:
            print(f"❌ Method 2 error: {e}")
            return False
    
    async def method_3_api_discovery(self):
        """Method 3: Look for API endpoints"""
        print("🔍 Attempting Method 3: API Discovery...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            
            try:
                page = await browser.new_page()
                
                # Intercept network requests
                api_endpoints = []
                
                def handle_request(request):
                    url = request.url
                    if any(keyword in url for keyword in ['api', 'graphql', 'rest', 'cart', 'auth']):
                        api_endpoints.append({
                            'url': url,
                            'method': request.method,
                            'headers': dict(request.headers)
                        })
                
                page.on('request', handle_request)
                
                # Navigate and trigger requests
                await page.goto("https://www.zehrs.ca/en", wait_until='networkidle')
                await page.wait_for_timeout(5000)
                
                if api_endpoints:
                    print(f"🎯 Discovered {len(api_endpoints)} API endpoints:")
                    for endpoint in api_endpoints[:5]:  # Show first 5
                        print(f"  {endpoint['method']} {endpoint['url']}")
                    
                    # Save API info
                    api_file = "/home/magi/clawd/grocery-data/zehrs_api_discovery.json"
                    with open(api_file, 'w') as f:
                        json.dump(api_endpoints, f, indent=2)
                    
                    print(f"💾 API endpoints saved to: {api_file}")
                    return api_endpoints
                else:
                    print("❌ No API endpoints discovered")
                    return []
                    
            except Exception as e:
                print(f"❌ Method 3 error: {e}")
                return []
            finally:
                await browser.close()
    
    async def method_4_mobile_app_simulation(self):
        """Method 4: Simulate mobile app requests"""
        print("📱 Attempting Method 4: Mobile App Simulation...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            
            try:
                # Mobile context
                iphone = p.devices['iPhone 13']
                context = await browser.new_context(**iphone)
                page = await context.new_page()
                
                print("📱 Navigating as mobile device...")
                await page.goto("https://www.zehrs.ca/en/sign-in", wait_until='networkidle')
                
                # Mobile sites sometimes have different auth flows
                title = await page.title()
                print(f"📱 Mobile page title: {title}")
                
                # Try mobile-specific login
                mobile_success = await self.attempt_login_forms(page, mobile=True)
                
                if mobile_success:
                    print("✅ Method 4 successful - mobile auth worked!")
                    return True
                    
            except Exception as e:
                print(f"❌ Method 4 error: {e}")
                return False
            finally:
                await browser.close()
        
        return False
    
    async def attempt_login_forms(self, page, mobile=False):
        """Try different login form strategies"""
        try:
            # Strategy 1: Wait for form and fill slowly (human-like)
            print("📝 Looking for login form...")
            
            email_selectors = [
                'input[type="email"]', 'input[name="email"]', '#email', 
                'input[placeholder*="email"]', '[data-testid="email"]'
            ]
            
            password_selectors = [
                'input[type="password"]', 'input[name="password"]', '#password',
                '[data-testid="password"]'
            ]
            
            # Find email field
            email_field = None
            for selector in email_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    email_field = selector
                    break
                except:
                    continue
            
            if not email_field:
                print("❌ Email field not found")
                return False
            
            # Find password field
            password_field = None
            for selector in password_selectors:
                try:
                    element = page.locator(selector)
                    if await element.count() > 0:
                        password_field = selector
                        break
                except:
                    continue
            
            if not password_field:
                print("❌ Password field not found")
                return False
            
            print(f"✅ Found login form - email: {email_field}, password: {password_field}")
            
            # Human-like typing
            await page.type(email_field, self.email, delay=100)
            await page.wait_for_timeout(1000)
            
            await page.type(password_field, self.password, delay=100)
            await page.wait_for_timeout(2000)
            
            # Find and click submit button
            submit_selectors = [
                'button[type="submit"]', 'input[type="submit"]',
                'button:has-text("Sign In")', 'button:has-text("Log In")',
                '[data-testid="submit"]', '.login-button', '.submit-button'
            ]
            
            submit_clicked = False
            for selector in submit_selectors:
                try:
                    element = page.locator(selector)
                    if await element.count() > 0:
                        await element.click()
                        submit_clicked = True
                        print(f"✅ Clicked submit button: {selector}")
                        break
                except:
                    continue
            
            if not submit_clicked:
                # Try Enter key
                await page.keyboard.press('Enter')
                print("⌨️ Tried Enter key")
            
            # Wait for navigation or error
            await page.wait_for_timeout(5000)
            
            # Check if login was successful
            current_url = page.url
            title = await page.title()
            
            # Success indicators
            success_indicators = [
                "sign-in" not in current_url.lower(),
                "login" not in current_url.lower(),
                "dashboard" in current_url.lower(),
                "account" in current_url.lower(),
                any(word in title.lower() for word in ['welcome', 'account', 'dashboard'])
            ]
            
            if any(success_indicators):
                print("✅ Login appears successful!")
                return True
            else:
                print(f"❌ Login may have failed - URL: {current_url}, Title: {title}")
                return False
                
        except Exception as e:
            print(f"❌ Login form error: {e}")
            return False
    
    async def solve_authentication(self):
        """Master method - try all approaches"""
        print("🔐 ZEHRS AUTHENTICATION SOLVER")
        print("=" * 40)
        print(f"Account: {self.email}")
        print()
        
        methods = [
            ("Session Restore", self.method_2_session_persistence),
            ("API Discovery", self.method_3_api_discovery),  
            ("Stealth Login", self.method_1_stealth_login),
            ("Mobile Simulation", self.method_4_mobile_app_simulation),
        ]
        
        for method_name, method_func in methods:
            print(f"\\n🔄 Trying: {method_name}")
            print("-" * 30)
            
            try:
                result = await method_func()
                if result:
                    print(f"🎉 SUCCESS! {method_name} worked!")
                    return True
                else:
                    print(f"❌ {method_name} failed")
            except Exception as e:
                print(f"❌ {method_name} error: {e}")
            
            print(f"⏳ Waiting 5 seconds before next method...")
            await asyncio.sleep(5)
        
        print("\\n❌ All authentication methods failed")
        print("\\n💡 Recommendations:")
        print("1. Check if 2FA is enabled on your account")
        print("2. Try logging in manually first to solve any CAPTCHAs")
        print("3. Consider using browser extension approach")
        print("4. Email receipt parsing might be more reliable")
        
        return False

# CLI interface
async def main():
    solver = ZehrsAuthSolver()
    
    if not solver.email or not solver.password:
        print("❌ No Zehrs credentials found in shared secrets")
        return
    
    success = await solver.solve_authentication()
    
    if success:
        print("\\n🎯 Authentication solved! You can now:")
        print("  - Access your cart programmatically")
        print("  - Scrape purchase history")
        print("  - Automate shopping tasks")
    else:
        print("\\n🔄 Authentication challenge remains unsolved")
        print("Consider alternative approaches or manual assistance")

if __name__ == "__main__":
    asyncio.run(main())