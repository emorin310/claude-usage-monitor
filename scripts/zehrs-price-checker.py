#!/usr/bin/env python3
"""
Zehrs Price Checker - No Login Required
Basic price checking and product search functionality
"""

import asyncio
import json
import sys
from datetime import datetime
from playwright.async_api import async_playwright

class ZehrsPriceChecker:
    
    async def search_products(self, query, limit=20):
        """Search for products without login (public search)"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
            )
            
            try:
                page = await browser.new_page()
                page.set_default_timeout(45000)
                
                # Set realistic user agent
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                print(f"🔍 Searching Zehrs for: {query}")
                
                # Go to search page  
                search_url = f"https://www.zehrs.ca/en/search?search-bar={query.replace(' ', '%20')}"
                await page.goto(search_url, wait_until='load')
                await page.wait_for_timeout(5000)  # Wait for dynamic content
                
                print("📄 Page loaded, extracting product data...")
                
                # Take screenshot for debugging
                await page.screenshot(path=f'/home/magi/clawd/search-{query.replace(" ", "-")}.png')
                
                # Extract products with multiple fallback strategies
                products = await page.evaluate(f'''() => {{
                    const items = [];
                    
                    // Strategy 1: Look for common product container patterns
                    const containerSelectors = [
                        '[data-testid*="product"]',
                        '.product-tile',
                        '.product-item', 
                        '.product-card',
                        '[class*="product"]',
                        '[data-track*="product"]',
                        'article',
                        '.tile'
                    ];
                    
                    let containers = [];
                    for (const selector of containerSelectors) {{
                        containers = document.querySelectorAll(selector);
                        console.log(`Selector "${{selector}}" found ${{containers.length}} elements`);
                        if (containers.length > 0) break;
                    }}
                    
                    if (containers.length === 0) {{
                        // Fallback: Look for any element with price-like text
                        containers = Array.from(document.querySelectorAll('*')).filter(el => {{
                            const text = el.textContent || '';
                            return text.includes('$') && text.match(/\\$\\d+\\.\\d{{2}}/);
                        }});
                        console.log(`Fallback price search found ${{containers.length}} elements`);
                    }}
                    
                    containers.forEach((container, index) => {{
                        if (index >= {limit}) return;
                        
                        // Extract text content
                        let text = container.textContent?.trim() || '';
                        if (text.length < 3) return;
                        
                        // Find title (look for meaningful text)
                        let title = '';
                        const titleSelectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '[class*="title"]', '[data-testid*="title"]'];
                        for (const sel of titleSelectors) {{
                            const elem = container.querySelector(sel);
                            if (elem && elem.textContent?.trim()?.length > 3) {{
                                title = elem.textContent.trim();
                                break;
                            }}
                        }}
                        
                        // If no specific title found, extract from full text
                        if (!title && text.length > 0) {{
                            // Try to extract product name from beginning of text
                            const lines = text.split('\\n').filter(line => line.trim().length > 3);
                            title = lines[0] || text.substring(0, 100);
                        }}
                        
                        // Find price
                        let price = '';
                        const priceRegex = /\\$\\d+\\.\\d{{2}}/g;
                        const priceMatches = text.match(priceRegex);
                        if (priceMatches) {{
                            price = priceMatches[0]; // Take first price found
                        }}
                        
                        // Try specific price selectors
                        if (!price) {{
                            const priceSelectors = ['.price', '[class*="price"]', '[data-testid*="price"]', '.cost', '.pricing'];
                            for (const sel of priceSelectors) {{
                                const elem = container.querySelector(sel);
                                if (elem) {{
                                    const priceText = elem.textContent?.trim();
                                    if (priceText && priceText.includes('$')) {{
                                        price = priceText;
                                        break;
                                    }}
                                }}
                            }}
                        }}
                        
                        // Get link
                        const link = container.querySelector('a')?.href || '';
                        
                        // Only add if we found meaningful content
                        if (title && title.length > 3) {{
                            items.push({{
                                title: title,
                                price: price || 'Price not available',
                                link: link,
                                rawText: text.substring(0, 200), // For debugging
                                index: index + 1
                            }});
                        }}
                    }});
                    
                    console.log(`Extracted ${{items.length}} products`);
                    return items;
                }}''')
                
                # Also get page title to confirm we're on right page
                page_title = await page.title()
                print(f"📋 Page title: {page_title}")
                
                if products:
                    print(f"✅ Found {len(products)} products")
                else:
                    print("⚠️ No products extracted - checking page content...")
                    
                    # Debug: Get page text to see what's available
                    page_text = await page.text_content('body')
                    if page_text and '$' in page_text:
                        print("💰 Page contains prices, but extraction failed")
                        print(f"📝 Sample content: {page_text[:300]}...")
                    else:
                        print("❌ Page may not have loaded properly or no prices visible")
                
                return products
                
            except Exception as e:
                print(f"❌ Search error: {str(e)}")
                return []
                
            finally:
                await browser.close()
    
    async def check_multiple_items(self, items):
        """Check prices for multiple items"""
        print(f"🛒 Checking prices for {len(items)} items...")
        results = {}
        
        for item in items:
            print(f"\\n--- {item} ---")
            products = await self.search_products(item, limit=5)
            results[item] = products
            
            if products:
                print(f"✅ Found {len(products)} options")
                for p in products[:2]:  # Show top 2
                    print(f"  • {p['title'][:50]}... - {p['price']}")
            else:
                print("❌ No products found")
            
            # Small delay between searches
            await asyncio.sleep(2)
        
        return results
    
    def save_results(self, results):
        """Save results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"zehrs_prices_{timestamp}.json"
        filepath = f"/home/magi/clawd/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Results saved to: {filepath}")
        return filepath

async def main():
    if len(sys.argv) < 2:
        print("🛒 Zehrs Price Checker")
        print("=" * 30)
        print("Usage:")
        print("  python zehrs-price-checker.py search <item>")
        print("  python zehrs-price-checker.py list <item1> <item2> ...")
        print("")
        print("Examples:")
        print("  python zehrs-price-checker.py search milk")
        print("  python zehrs-price-checker.py list milk bread eggs")
        return
    
    checker = ZehrsPriceChecker()
    command = sys.argv[1]
    
    if command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        products = await checker.search_products(query)
        
        if products:
            print(f"\\n🛒 Results for '{query}':")
            print("=" * 50)
            for p in products:
                print(f"{p['index']}. {p['title']}")
                print(f"   💰 {p['price']}")
                print(f"   🔗 {p['link'][:60]}..." if p['link'] else "   🔗 No link")
                print()
        
    elif command == "list" and len(sys.argv) > 2:
        items = sys.argv[2:]
        results = await checker.check_multiple_items(items)
        
        print("\\n📊 Summary Report:")
        print("=" * 40)
        for item, products in results.items():
            print(f"\\n🔍 {item.upper()}: {len(products)} options found")
            if products:
                best = products[0]  # Assume first is best match
                print(f"  👑 Best: {best['title'][:40]}... - {best['price']}")
        
        checker.save_results(results)
    
    else:
        print("❌ Invalid command")

if __name__ == "__main__":
    asyncio.run(main())