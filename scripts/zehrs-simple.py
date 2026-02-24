#!/usr/bin/env python3
"""
Simple Zehrs Browser Test - Optimized for server environment
"""

import asyncio
import os
from playwright.async_api import async_playwright

async def test_zehrs_simple():
    """Simple test to access Zehrs homepage"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions'
            ]
        )
        
        try:
            page = await browser.new_page()
            
            # Set longer timeout and user agent
            page.set_default_timeout(60000)  # 60 seconds
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            print("🌐 Testing Zehrs homepage access...")
            await page.goto("https://www.zehrs.ca/", wait_until='load')
            
            title = await page.title()
            url = page.url
            
            print(f"✅ Success! Page title: {title}")
            print(f"📍 Final URL: {url}")
            
            # Take a small screenshot
            await page.screenshot(path='/home/magi/clawd/zehrs-homepage.png', full_page=False)
            print("📸 Homepage screenshot saved")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
            
        finally:
            await browser.close()

async def test_zehrs_search_page():
    """Test accessing search/product pages without login"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(60000)
            
            print("🔍 Testing Zehrs search functionality...")
            await page.goto("https://www.zehrs.ca/en/search?search-bar=milk", wait_until='load')
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            title = await page.title()
            content_snippet = await page.text_content('body')
            
            print(f"📄 Search page title: {title}")
            if content_snippet:
                print(f"📝 Content preview: {content_snippet[:200]}...")
            
            await page.screenshot(path='/home/magi/clawd/zehrs-search.png')
            print("📸 Search page screenshot saved")
            
            return True
            
        except Exception as e:
            print(f"❌ Search test error: {str(e)}")
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    print("🧪 Zehrs Browser Test - Simple Version")
    print("=" * 40)
    
    # Test 1: Homepage access
    result1 = asyncio.run(test_zehrs_simple())
    
    if result1:
        print("\n" + "=" * 40)
        # Test 2: Search functionality
        result2 = asyncio.run(test_zehrs_search_page())
        
        if result2:
            print("\n✅ Both tests passed! Playwright + Zehrs is working!")
            print("🎯 Ready to implement full grocery automation!")
        else:
            print("\n⚠️ Homepage works, but search had issues")
    else:
        print("\n❌ Basic connection failed - need to debug further")