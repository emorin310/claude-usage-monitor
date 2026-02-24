#!/usr/bin/env python3
"""
Zehrs Browser Automation Script
Automates grocery shopping on Zehrs.ca using Playwright
"""

import asyncio
import os
from playwright.async_api import async_playwright

# Load credentials from shared secrets
def load_credentials():
    secrets_path = "/mnt/bigstore/knowledge/shared/secrets.env"
    creds = {}
    
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    creds[key] = value
    
    return creds.get('ZEHRS_EMAIL'), creds.get('ZEHRS_PASSWORD')

async def test_zehrs_login():
    """Test login to Zehrs and basic navigation"""
    
    email, password = load_credentials()
    if not email or not password:
        print("❌ No Zehrs credentials found in shared secrets")
        return False
    
    print(f"🔐 Testing Zehrs login for: {email}")
    
    async with async_playwright() as p:
        # Launch browser in headless mode (required for server environment)
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        
        try:
            page = await browser.new_page()
            print("🌐 Navigating to Zehrs sign-in page...")
            
            # Go to sign-in page
            await page.goto("https://www.zehrs.ca/en/sign-in", wait_until='networkidle')
            
            # Wait for and fill login form
            print("📝 Filling login credentials...")
            await page.wait_for_selector('input[type="email"], input[name="email"], #email')
            await page.fill('input[type="email"], input[name="email"], #email', email)
            
            await page.wait_for_selector('input[type="password"], input[name="password"], #password')
            await page.fill('input[type="password"], input[name="password"], #password', password)
            
            # Submit login
            print("🔑 Submitting login...")
            await page.click('button[type="submit"], input[type="submit"], .submit-button')
            
            # Wait for navigation or error
            await page.wait_for_timeout(3000)
            
            # Check if we're logged in
            current_url = page.url
            page_title = await page.title()
            
            print(f"📍 Current URL: {current_url}")
            print(f"📄 Page title: {page_title}")
            
            # Try to access "My Shop" to verify login
            print("🛒 Navigating to My Shop...")
            await page.goto("https://www.zehrs.ca/en/collection/my-shop", wait_until='networkidle')
            
            # Take screenshot for debugging
            await page.screenshot(path='/home/magi/clawd/zehrs-test.png', full_page=True)
            print("📸 Screenshot saved as zehrs-test.png")
            
            # Get page content snippet
            content = await page.text_content('body')
            if content and len(content) > 200:
                print(f"✅ Successfully accessed Zehrs! Page content preview:")
                print(content[:500] + "...")
                return True
            else:
                print("❌ Unable to access Zehrs properly")
                return False
                
        except Exception as e:
            print(f"❌ Error during Zehrs access: {str(e)}")
            return False
            
        finally:
            await browser.close()

async def search_products(query="milk"):
    """Search for products on Zehrs"""
    
    email, password = load_credentials()
    if not email or not password:
        print("❌ No credentials available")
        return []
    
    print(f"🔍 Searching for: {query}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        
        try:
            page = await browser.new_page()
            
            # Quick login (simplified for product search)
            await page.goto("https://www.zehrs.ca/en/sign-in")
            await page.wait_for_selector('input[type="email"]', timeout=10000)
            await page.fill('input[type="email"]', email)
            await page.fill('input[type="password"]', password)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(3000)
            
            # Search for products
            await page.goto(f"https://www.zehrs.ca/en/search?search-bar={query}")
            await page.wait_for_timeout(2000)
            
            # Extract product information
            products = await page.evaluate('''() => {
                const items = [];
                const productCards = document.querySelectorAll('[data-testid="product-tile"], .product-tile, .product-item');
                
                productCards.forEach(card => {
                    const title = card.querySelector('h3, .product-title, [data-testid="product-title"]')?.textContent?.trim();
                    const price = card.querySelector('.price, [data-testid="price"]')?.textContent?.trim();
                    const link = card.querySelector('a')?.href;
                    
                    if (title && price) {
                        items.push({
                            title: title,
                            price: price,
                            link: link
                        });
                    }
                });
                
                return items.slice(0, 10); // Return top 10 results
            }''')
            
            return products
            
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            return []
            
        finally:
            await browser.close()

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            result = asyncio.run(test_zehrs_login())
            sys.exit(0 if result else 1)
            
        elif command == "search" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            products = asyncio.run(search_products(query))
            
            print(f"\n🛒 Search results for '{query}':")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product['title']}")
                print(f"   Price: {product['price']}")
                if product['link']:
                    print(f"   Link: {product['link']}")
                print()
                
        else:
            print("Usage:")
            print("  python zehrs-browser.py test")
            print("  python zehrs-browser.py search <query>")
    else:
        # Default: test login
        asyncio.run(test_zehrs_login())