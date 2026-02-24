#!/usr/bin/env python3
"""
Grocery Assistant - Full Zehrs.ca Automation
Handles login, shopping lists, price tracking, and cart management
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright

class GroceryAssistant:
    def __init__(self):
        self.email, self.password = self.load_credentials()
        
    def load_credentials(self):
        """Load credentials from shared secrets"""
        secrets_path = "/mnt/bigstore/knowledge/shared/secrets.env"
        
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
        return None, None
    
    async def login(self, page):
        """Login to Zehrs account"""
        try:
            print("🔐 Logging in to Zehrs...")
            await page.goto("https://www.zehrs.ca/en/sign-in", wait_until='load')
            await page.wait_for_timeout(2000)
            
            # Find and fill email field
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]', 
                '#email',
                'input[data-testid="email"]'
            ]
            
            for selector in email_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.fill(selector, self.email)
                    print(f"✅ Email filled using selector: {selector}")
                    break
                except:
                    continue
            
            # Find and fill password field
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                '#password',
                'input[data-testid="password"]'
            ]
            
            for selector in password_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.fill(selector, self.password)
                    print(f"✅ Password filled using selector: {selector}")
                    break
                except:
                    continue
            
            # Submit form
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Sign In")',
                'button:has-text("Log In")',
                '.submit-button'
            ]
            
            for selector in submit_selectors:
                try:
                    await page.click(selector)
                    print(f"✅ Login submitted using: {selector}")
                    break
                except:
                    continue
            
            # Wait for login to complete
            await page.wait_for_timeout(5000)
            
            # Check if login was successful
            current_url = page.url
            if "sign-in" not in current_url.lower():
                print("✅ Login successful!")
                return True
            else:
                print("⚠️ Login may not have completed - still on sign-in page")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    async def search_products(self, query, limit=20):
        """Search for products and return results"""
        
        if not self.email or not self.password:
            print("❌ No credentials available for product search")
            return []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                page = await browser.new_page()
                page.set_default_timeout(60000)
                
                # Login first
                if await self.login(page):
                    print(f"🔍 Searching for: {query}")
                    
                    # Navigate to search results
                    search_url = f"https://www.zehrs.ca/en/search?search-bar={query.replace(' ', '%20')}"
                    await page.goto(search_url, wait_until='load')
                    await page.wait_for_timeout(3000)
                    
                    # Extract product information
                    products = await page.evaluate(f'''() => {{
                        const items = [];
                        
                        // Try multiple selectors for product cards
                        const selectors = [
                            '[data-testid="product-tile"]',
                            '.product-tile',
                            '.product-item',
                            '.product-card',
                            '[data-track*="product"]'
                        ];
                        
                        let productCards = [];
                        for (const selector of selectors) {{
                            productCards = document.querySelectorAll(selector);
                            if (productCards.length > 0) break;
                        }}
                        
                        productCards.forEach((card, index) => {{
                            if (index >= {limit}) return;
                            
                            // Extract title
                            const titleSelectors = ['h3', '.product-title', '[data-testid="product-title"]', '.title'];
                            let title = '';
                            for (const sel of titleSelectors) {{
                                const elem = card.querySelector(sel);
                                if (elem) {{
                                    title = elem.textContent?.trim();
                                    break;
                                }}
                            }}
                            
                            // Extract price
                            const priceSelectors = ['.price', '[data-testid="price"]', '.pricing', '.cost'];
                            let price = '';
                            for (const sel of priceSelectors) {{
                                const elem = card.querySelector(sel);
                                if (elem) {{
                                    price = elem.textContent?.trim();
                                    break;
                                }}
                            }}
                            
                            // Extract link
                            const link = card.querySelector('a')?.href;
                            
                            if (title) {{
                                items.push({{
                                    title: title,
                                    price: price || 'Price not found',
                                    link: link || '',
                                    index: index + 1
                                }});
                            }}
                        }});
                        
                        return items;
                    }}''')
                    
                    # Save screenshot for debugging
                    await page.screenshot(path=f'/home/magi/clawd/search-{query.replace(" ", "-")}.png')
                    
                    return products
                else:
                    print("❌ Could not login - search aborted")
                    return []
                    
            except Exception as e:
                print(f"❌ Search error: {str(e)}")
                return []
                
            finally:
                await browser.close()
    
    async def get_shopping_list_recommendations(self, shopping_list):
        """Get product recommendations for a shopping list"""
        
        print(f"🛒 Processing shopping list: {shopping_list}")
        all_results = {}
        
        for item in shopping_list:
            print(f"\n--- Searching for: {item} ---")
            products = await self.search_products(item, limit=5)
            
            if products:
                all_results[item] = products
                print(f"✅ Found {len(products)} options for '{item}'")
            else:
                all_results[item] = []
                print(f"❌ No results found for '{item}'")
            
            # Small delay between searches
            await asyncio.sleep(1)
        
        return all_results
    
    def save_results(self, results, filename=None):
        """Save search results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"grocery_search_{timestamp}.json"
        
        filepath = f"/home/magi/clawd/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {filepath}")
        return filepath

# CLI Interface
async def main():
    assistant = GroceryAssistant()
    
    if len(sys.argv) < 2:
        print("🛒 Grocery Assistant - Zehrs.ca Automation")
        print("=" * 45)
        print("Usage:")
        print("  python grocery-assistant.py search <item>")
        print("  python grocery-assistant.py list <item1> <item2> <item3>")
        print("")
        print("Examples:")
        print("  python grocery-assistant.py search milk")
        print("  python grocery-assistant.py list milk bread eggs cheese")
        return
    
    command = sys.argv[1]
    
    if command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        products = await assistant.search_products(query)
        
        if products:
            print(f"\\n🛒 Search Results for '{query}':")
            print("=" * 50)
            
            for product in products:
                print(f"{product['index']}. {product['title']}")
                print(f"   💰 {product['price']}")
                if product['link']:
                    print(f"   🔗 {product['link']}")
                print()
        else:
            print(f"❌ No products found for '{query}'")
    
    elif command == "list" and len(sys.argv) > 2:
        shopping_list = sys.argv[2:]
        results = await assistant.get_shopping_list_recommendations(shopping_list)
        
        print("\\n🛒 Shopping List Results:")
        print("=" * 50)
        
        total_items = 0
        for item, products in results.items():
            print(f"\\n📦 {item.upper()}:")
            if products:
                for i, product in enumerate(products[:3], 1):  # Show top 3
                    print(f"  {i}. {product['title']}")
                    print(f"     💰 {product['price']}")
                total_items += len(products)
            else:
                print("  ❌ No results found")
        
        print(f"\\n📊 Summary: Found {total_items} total product options")
        
        # Save results
        assistant.save_results(results)
    
    else:
        print("❌ Invalid command. Use 'search' or 'list'.")

if __name__ == "__main__":
    asyncio.run(main())