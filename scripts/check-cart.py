#!/usr/bin/env python3
"""
Zehrs Cart Checker - Attempt to retrieve current cart contents
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

async def check_current_cart():
    """Attempt to access and retrieve current cart from Zehrs"""
    
    # Load credentials
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
    
    if not email or not password:
        print("❌ No Zehrs credentials found")
        return
    
    print(f"🔐 Attempting to access cart for: {email}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        try:
            page = await browser.new_page()
            page.set_default_timeout(30000)
            
            # Try to access cart page directly first
            print("🛒 Checking cart page...")
            try:
                await page.goto("https://www.zehrs.ca/en/cart", wait_until='load')
                await page.wait_for_timeout(3000)
                
                title = await page.title()
                print(f"📄 Page title: {title}")
                
                # Check if we're redirected to login
                current_url = page.url
                if "sign-in" in current_url or "login" in current_url:
                    print("🔒 Redirected to login - attempting authentication...")
                    
                    # Fill login form
                    try:
                        await page.fill('input[type="email"]', email)
                        await page.fill('input[type="password"]', password)
                        await page.click('button[type="submit"]')
                        await page.wait_for_timeout(5000)
                        
                        # Check if login successful
                        new_url = page.url
                        if "cart" in new_url:
                            print("✅ Login successful, now checking cart...")
                        else:
                            print("⚠️ Login may have failed or requires additional verification")
                    except Exception as login_error:
                        print(f"❌ Login error: {login_error}")
                        return
                
                # Extract cart contents
                cart_content = await page.text_content('body')
                
                if cart_content:
                    # Look for cart items and prices
                    import re
                    prices = re.findall(r'\$\d+\.\d{2}', cart_content)
                    
                    if "empty" in cart_content.lower() or "no items" in cart_content.lower():
                        print("🛒 Cart appears to be empty")
                        return {"items": [], "total": "$0.00", "status": "empty"}
                    
                    # Try to extract structured cart data
                    cart_data = await page.evaluate('''
                        () => {
                            const items = [];
                            let total = '';
                            
                            // Look for cart item containers
                            const itemSelectors = [
                                '[data-testid*="cart-item"]',
                                '.cart-item',
                                '.line-item',
                                '[class*="item"]'
                            ];
                            
                            let itemElements = [];
                            for (const selector of itemSelectors) {
                                itemElements = document.querySelectorAll(selector);
                                if (itemElements.length > 0) break;
                            }
                            
                            itemElements.forEach(element => {
                                const text = element.textContent || '';
                                const priceMatch = text.match(/\$\d+\.\d{2}/);
                                
                                if (text.length > 10 && priceMatch) {
                                    items.push({
                                        description: text.substring(0, 100),
                                        price: priceMatch[0]
                                    });
                                }
                            });
                            
                            // Look for total
                            const totalElement = document.querySelector('[data-testid*="total"], .total, .cart-total');
                            if (totalElement) {
                                const totalMatch = totalElement.textContent.match(/\$\d+\.\d{2}/);
                                if (totalMatch) total = totalMatch[0];
                            }
                            
                            return { items, total, timestamp: new Date().toISOString() };
                        }
                    ''')
                    
                    if cart_data['items'] and len(cart_data['items']) > 0:
                        print(f"🛒 Cart contains {len(cart_data['items'])} items:")
                        for i, item in enumerate(cart_data['items'], 1):
                            print(f"  {i}. {item['description'][:50]}... - {item['price']}")
                        
                        if cart_data['total']:
                            print(f"💰 Total: {cart_data['total']}")
                        else:
                            # Calculate total from individual prices
                            total = sum(float(item['price'].replace('$', '')) for item in cart_data['items'] if item['price'])
                            print(f"💰 Estimated Total: ${total:.2f}")
                        
                        # Save cart data
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        cart_file = f"/home/magi/clawd/grocery-data/cart/cart_{timestamp}.json"
                        
                        with open(cart_file, 'w') as f:
                            json.dump(cart_data, f, indent=2)
                        
                        print(f"💾 Cart data saved to: {cart_file}")
                        return cart_data
                    
                    else:
                        print("🛒 No cart items found - cart may be empty or page didn't load properly")
                        return {"items": [], "total": "$0.00", "status": "empty_or_error"}
                
                else:
                    print("❌ Could not read cart page content")
                    return None
                    
            except Exception as cart_error:
                print(f"❌ Cart access error: {cart_error}")
                return None
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(check_current_cart())
    
    if result is None:
        print("\n❌ Unable to access cart - authentication or technical issues")
        print("💡 This typically happens due to:")
        print("   • CAPTCHA verification required")
        print("   • 2-factor authentication")
        print("   • Session expired")
        print("   • Anti-bot protection")
        print("\n🔧 Alternative: Manually check your cart and I can help track it!")
    elif result.get("status") == "empty":
        print("\n🛒 Your Zehrs cart is currently empty")
    elif result and result.get("items"):
        print(f"\n📊 CART SUMMARY:")
        print(f"   Items: {len(result['items'])}")
        print(f"   Total: {result.get('total', 'Not found')}")