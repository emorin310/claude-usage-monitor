#!/usr/bin/env python3
"""
Modern Auth Approach - Handle modal/popup login
"""

import asyncio
from playwright.async_api import async_playwright

async def modern_login_attempt():
    """Handle modern modal/popup based login"""
    
    print("🔐 MODERN AUTHENTICATION APPROACH")
    print("=" * 40)
    print("Handling modal/popup login systems...")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(15000)
            
            print("1️⃣ Loading main Zehrs page...")
            await page.goto('https://www.zehrs.ca/en')
            await page.wait_for_timeout(3000)  # Wait for JavaScript to load
            
            print("2️⃣ Looking for login triggers...")
            
            # Common login trigger selectors
            login_triggers = [
                'text="Sign In"',
                'text="Log In"', 
                'text="Login"',
                '[data-testid="sign-in"]',
                '[data-testid="login"]',
                '.sign-in',
                '.login',
                'a[href*="sign-in"]',
                'button:has-text("Sign In")',
                '#sign-in-button'
            ]
            
            login_clicked = False
            for trigger in login_triggers:
                try:
                    element = page.locator(trigger).first
                    if await element.is_visible():
                        print(f"   ✅ Found login trigger: {trigger}")
                        await element.click()
                        print(f"   ✅ Clicked: {trigger}")
                        login_clicked = True
                        break
                except:
                    continue
            
            if not login_clicked:
                print("   ❌ No login trigger found - checking page content...")
                
                # Get page content to understand the structure
                content = await page.content()
                
                # Look for authentication indicators
                auth_indicators = ['sign-in', 'login', 'authentication', 'oauth', 'sso']
                found_indicators = []
                
                for indicator in auth_indicators:
                    if indicator in content.lower():
                        found_indicators.append(indicator)
                
                if found_indicators:
                    print(f"   📍 Found auth indicators: {', '.join(found_indicators)}")
                else:
                    print("   ❌ No obvious authentication system found")
                    
                # Take screenshot for debugging
                await page.screenshot(path='/home/magi/clawd/main-page-debug.png')
                print("   📸 Main page screenshot saved")
                
                return False
            
            print("3️⃣ Waiting for login form/modal to appear...")
            await page.wait_for_timeout(3000)
            
            # Look for login form after clicking
            form_selectors = [
                'form[action*="login"]',
                'form[action*="sign-in"]', 
                'input[type="email"]',
                'input[name="email"]',
                '#email'
            ]
            
            form_found = False
            for selector in form_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible():
                        print(f"   ✅ Login form appeared: {selector}")
                        form_found = True
                        break
                except:
                    continue
            
            if form_found:
                print("4️⃣ Attempting to fill login form...")
                
                # Try to fill credentials
                email = "emorin310@gmail.com"
                password = "opusER123!"
                
                try:
                    # Fill email
                    email_field = page.locator('input[type="email"], input[name="email"], #email').first
                    await email_field.fill(email)
                    print("   ✅ Email filled")
                    
                    # Fill password  
                    password_field = page.locator('input[type="password"], input[name="password"], #password').first
                    await password_field.fill(password)
                    print("   ✅ Password filled")
                    
                    # Submit
                    submit_button = page.locator('button[type="submit"], input[type="submit"], button:has-text("Sign In")').first
                    await submit_button.click()
                    print("   ✅ Form submitted")
                    
                    # Wait for response
                    await page.wait_for_timeout(5000)
                    
                    # Check if login succeeded
                    current_url = page.url
                    print(f"   📍 Current URL: {current_url}")
                    
                    # Look for success indicators
                    success_indicators = [
                        'text="Account"',
                        'text="My Account"', 
                        'text="Profile"',
                        'text="Sign Out"',
                        'text="Logout"'
                    ]
                    
                    login_success = False
                    for indicator in success_indicators:
                        try:
                            if await page.locator(indicator).first.is_visible():
                                print(f"   ✅ Login success indicator: {indicator}")
                                login_success = True
                                break
                        except:
                            continue
                    
                    if login_success:
                        print("🎉 LOGIN SUCCESSFUL!")
                        
                        # Now try to access cart
                        print("5️⃣ Accessing cart...")
                        await page.goto('https://www.zehrs.ca/en/cart')
                        await page.wait_for_timeout(3000)
                        
                        cart_title = await page.title()
                        print(f"   Cart page title: {cart_title}")
                        
                        # Take cart screenshot
                        await page.screenshot(path='/home/magi/clawd/cart-success.png')
                        print("   📸 Cart screenshot saved")
                        
                        return True
                    else:
                        print("❌ Login may have failed - no success indicators")
                        return False
                        
                except Exception as fill_error:
                    print(f"   ❌ Form filling error: {fill_error}")
                    return False
                    
            else:
                print("   ❌ No login form appeared after clicking trigger")
                
                # Take screenshot of current state
                await page.screenshot(path='/home/magi/clawd/after-click-debug.png') 
                print("   📸 After-click screenshot saved")
                
                return False
                
        except Exception as e:
            print(f"❌ Modern auth error: {e}")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(modern_login_attempt())
    
    if result:
        print("\n✅ MODERN AUTH SUCCESS!")
        print("🛒 Should now have cart access")
    else:
        print("\n❌ Modern auth failed")
        print("💡 Zehrs may use advanced authentication (SSO/OAuth)")