#!/usr/bin/env python3
"""
Simple Auth Check - Minimal approach
"""

import asyncio
from playwright.async_api import async_playwright

async def simple_login_attempt():
    """Simple login attempt with status reporting"""
    
    email = "emorin310@gmail.com" 
    password = "opusER123!"
    
    print("🔐 SIMPLE LOGIN ATTEMPT")
    print("=" * 30)
    print(f"Email: {email}")
    print("Attempting automated login...")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(15000)
            
            print("1️⃣ Loading sign-in page...")
            await page.goto('https://www.zehrs.ca/en/sign-in')
            
            print("2️⃣ Looking for login form...")
            # Check what's actually on the page
            title = await page.title()
            print(f"   Page title: {title}")
            
            # Take a screenshot to see what we're dealing with
            await page.screenshot(path='/home/magi/clawd/login-debug.png')
            print("   📸 Screenshot saved: login-debug.png")
            
            # Look for form fields
            email_field = await page.query_selector('input[type="email"]')
            if email_field:
                print("   ✅ Email field found")
                await email_field.fill(email)
                print("   ✅ Email entered")
            else:
                print("   ❌ No email field found")
                return False
            
            password_field = await page.query_selector('input[type="password"]')
            if password_field:
                print("   ✅ Password field found") 
                await password_field.fill(password)
                print("   ✅ Password entered")
            else:
                print("   ❌ No password field found")
                return False
            
            print("3️⃣ Submitting form...")
            submit_btn = await page.query_selector('button[type="submit"]')
            if submit_btn:
                await submit_btn.click()
                print("   ✅ Submit button clicked")
            else:
                await page.keyboard.press('Enter')
                print("   ⌨️ Enter key pressed")
            
            print("4️⃣ Waiting for response...")
            await page.wait_for_timeout(5000)
            
            # Check result
            final_url = page.url
            final_title = await page.title()
            
            print(f"   Final URL: {final_url}")
            print(f"   Final title: {final_title}")
            
            if 'sign-in' not in final_url:
                print("✅ LOGIN SUCCESS!")
                
                # Try to get cart
                print("5️⃣ Checking cart...")
                await page.goto('https://www.zehrs.ca/en/cart')
                cart_title = await page.title()
                print(f"   Cart page: {cart_title}")
                
                # Take cart screenshot
                await page.screenshot(path='/home/magi/clawd/cart-debug.png')
                print("   📸 Cart screenshot: cart-debug.png")
                
                return True
            else:
                print("❌ LOGIN FAILED - still on sign-in page")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_login_attempt())