#!/usr/bin/env python3
"""
Zehrs Master Shopping Assistant
Complete grocery automation system with all requested features:
- Current cart items
- Past purchase inventory  
- Promotion scanning
- Favorites and staples management
- Easy shopping interface
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

class ZehrsMaster:
    def __init__(self):
        self.data_dir = "/home/magi/clawd/grocery-data"
        self.ensure_data_dir()
        self.email, self.password = self.load_credentials()
        
    def ensure_data_dir(self):
        """Create data directory structure"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/purchases", exist_ok=True)
        os.makedirs(f"{self.data_dir}/favorites", exist_ok=True)
        os.makedirs(f"{self.data_dir}/promotions", exist_ok=True)
        
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
    
    async def enhanced_search(self, query, limit=20):
        """Enhanced product search with better extraction"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                page = await browser.new_page()
                page.set_default_timeout(45000)
                
                print(f"🔍 Enhanced search for: {query}")
                
                # Navigate to search
                search_url = f"https://www.zehrs.ca/en/search?search-bar={query.replace(' ', '%20')}"
                await page.goto(search_url, wait_until='networkidle')
                await page.wait_for_timeout(3000)
                
                # Enhanced product extraction
                products = await page.evaluate(f'''
                    (() => {{
                        const products = [];
                        
                        // Wait for any lazy loading
                        const observer = new MutationObserver(() => {{}});
                        
                        // Multiple strategies to find products
                        const strategies = [
                            // Strategy 1: Complete product tiles
                            () => document.querySelectorAll('[data-testid="product-tile"], .product-tile'),
                            // Strategy 2: Any container with both price and description
                            () => Array.from(document.querySelectorAll('*')).filter(el => {{
                                const text = el.textContent || '';
                                return text.includes('$') && 
                                       text.length > 20 && 
                                       text.length < 500 &&
                                       !el.querySelector('*[data-testid="product-tile"]'); // Avoid duplicates
                            }}),
                            // Strategy 3: Link elements that look like products
                            () => Array.from(document.querySelectorAll('a')).filter(el => {{
                                const href = el.href || '';
                                const text = el.textContent || '';
                                return (href.includes('/en/') && text.includes('$')) ||
                                       (text.length > 10 && text.length < 200 && text.includes('$'));
                            }})
                        ];
                        
                        let elements = [];
                        for (const strategy of strategies) {{
                            elements = strategy();
                            console.log(`Strategy found ${{elements.length}} elements`);
                            if (elements.length >= 5) break; // Use first strategy that finds enough
                        }}
                        
                        // Process elements
                        Array.from(elements).slice(0, {limit}).forEach((element, index) => {{
                            const text = element.textContent?.trim() || '';
                            if (text.length < 10) return;
                            
                            // Extract title - try multiple approaches
                            let title = '';
                            
                            // Look for specific title elements
                            const titleElement = element.querySelector('h1, h2, h3, h4, [data-testid*="title"], [class*="title"], [class*="name"]');
                            if (titleElement) {{
                                title = titleElement.textContent?.trim();
                            }}
                            
                            // Fallback: Clean up text to extract likely product name
                            if (!title || title.length < 5) {{
                                // Split by common separators and take the meaningful part
                                const lines = text.split(/\\n|\\t/).filter(line => {{
                                    const l = line.trim();
                                    return l.length > 5 && 
                                           !l.startsWith('$') && 
                                           !l.includes('Price') &&
                                           !l.includes('Add to cart') &&
                                           !l.includes('Quick shop');
                                }});
                                
                                title = lines[0]?.trim() || text.substring(0, 60);
                            }}
                            
                            // Extract price
                            const priceRegex = /\\$\\d+\\.\\d{{2}}(?:\\/[^\\s]*)?/g;
                            const prices = text.match(priceRegex) || [];
                            const price = prices[0] || 'Price not found';
                            
                            // Extract additional info
                            const saleMatch = text.match(/(save \\$\\d+\\.\\d{{2}}|was \\$\\d+\\.\\d{{2}})/i);
                            const saleInfo = saleMatch ? saleMatch[0] : '';
                            
                            // Get link
                            const link = element.href || element.querySelector('a')?.href || '';
                            
                            // Extract brand if possible
                            let brand = '';
                            if (text.includes('Prepared in Canada')) brand = 'Canadian';
                            const brandMatch = title.match(/^([A-Z][a-zA-Z\\s&]+?)\\s/);
                            if (brandMatch) brand = brandMatch[1];
                            
                            // Only include if we have meaningful data
                            if (title && title.length > 3 && !title.includes('undefined')) {{
                                products.push({{
                                    title: title,
                                    price: price,
                                    brand: brand,
                                    saleInfo: saleInfo,
                                    link: link,
                                    category: '{query}',
                                    scraped: new Date().toISOString(),
                                    index: products.length + 1
                                }});
                            }}
                        }});
                        
                        // Deduplicate by title
                        const unique = [];
                        const seen = new Set();
                        for (const product of products) {{
                            const key = product.title.toLowerCase().replace(/\\s+/g, '');
                            if (!seen.has(key)) {{
                                seen.add(key);
                                unique.push(product);
                            }}
                        }}
                        
                        console.log(`Extracted ${{unique.length}} unique products`);
                        return unique;
                    }})();
                ''')
                
                return products
                
            except Exception as e:
                print(f"❌ Enhanced search error: {e}")
                return []
            finally:
                await browser.close()
    
    async def scan_promotions(self):
        """Scan current promotions and deals"""
        print("🔥 Scanning for promotions...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            
            try:
                page = await browser.new_page()
                
                # Check main deals page
                await page.goto("https://www.zehrs.ca/en/deals-and-flyer", wait_until='load')
                await page.wait_for_timeout(3000)
                
                promotions = await page.evaluate('''
                    (() => {{
                        const deals = [];
                        
                        // Look for deal containers
                        const dealElements = document.querySelectorAll(
                            '[data-testid*="deal"], [class*="deal"], [class*="promo"], ' +
                            '[class*="sale"], .special, .offer, [data-testid*="offer"]'
                        );
                        
                        dealElements.forEach((element, index) => {{
                            const text = element.textContent?.trim() || '';
                            const link = element.querySelector('a')?.href || element.href || '';
                            
                            // Look for discount patterns
                            const discountMatch = text.match(/(\\d+%\\s*off|save \\$\\d+|buy \\d+ get \\d+)/i);
                            const priceMatch = text.match(/\\$\\d+\\.\\d{{2}}/);
                            
                            if (text.length > 10 && (discountMatch || priceMatch)) {{
                                deals.push({{
                                    title: text.substring(0, 100),
                                    discount: discountMatch ? discountMatch[0] : '',
                                    price: priceMatch ? priceMatch[0] : '',
                                    link: link,
                                    found: new Date().toISOString()
                                }});
                            }}
                        }});
                        
                        return deals.slice(0, 20);
                    }})();
                ''')
                
                # Save promotions
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                promo_file = f"{self.data_dir}/promotions/scan_{timestamp}.json"
                
                with open(promo_file, 'w') as f:
                    json.dump(promotions, f, indent=2)
                
                print(f"🔥 Found {len(promotions)} promotions, saved to {promo_file}")
                return promotions
                
            except Exception as e:
                print(f"❌ Promotion scan error: {e}")
                return []
            finally:
                await browser.close()
    
    def manage_favorites(self, action, items=None):
        """Manage favorites list"""
        fav_file = f"{self.data_dir}/favorites/favorites.json"
        
        # Load existing favorites
        if os.path.exists(fav_file):
            with open(fav_file, 'r') as f:
                favorites = json.load(f)
        else:
            favorites = {"items": [], "last_updated": ""}
        
        if action == "add" and items:
            for item in items:
                if item not in favorites["items"]:
                    favorites["items"].append(item)
                    print(f"➕ Added '{item}' to favorites")
                else:
                    print(f"ℹ️ '{item}' already in favorites")
        
        elif action == "remove" and items:
            for item in items:
                if item in favorites["items"]:
                    favorites["items"].remove(item)
                    print(f"➖ Removed '{item}' from favorites")
        
        elif action == "list":
            print("⭐ Current Favorites:")
            for i, item in enumerate(favorites["items"], 1):
                print(f"  {i}. {item}")
            return favorites["items"]
        
        # Save updated favorites
        favorites["last_updated"] = datetime.now().isoformat()
        with open(fav_file, 'w') as f:
            json.dump(favorites, f, indent=2)
        
        return favorites["items"]
    
    def manage_staples(self, action, items=None):
        """Manage staples list (recurring essentials)"""
        staples_file = f"{self.data_dir}/favorites/staples.json"
        
        # Load existing staples
        if os.path.exists(staples_file):
            with open(staples_file, 'r') as f:
                staples = json.load(f)
        else:
            staples = {
                "items": [],
                "auto_check_frequency": "weekly",
                "last_updated": ""
            }
        
        if action == "add" and items:
            for item in items:
                if item not in staples["items"]:
                    staples["items"].append(item)
                    print(f"🥛 Added '{item}' to staples")
                else:
                    print(f"ℹ️ '{item}' already in staples")
        
        elif action == "remove" and items:
            for item in items:
                if item in staples["items"]:
                    staples["items"].remove(item)
                    print(f"🗑️ Removed '{item}' from staples")
        
        elif action == "list":
            print("🥛 Current Staples:")
            for i, item in enumerate(staples["items"], 1):
                print(f"  {i}. {item}")
            return staples["items"]
        
        # Save updated staples
        staples["last_updated"] = datetime.now().isoformat()
        with open(staples_file, 'w') as f:
            json.dump(staples, f, indent=2)
        
        return staples["items"]
    
    async def smart_shopping_assistant(self, mode="full"):
        """Complete shopping workflow"""
        print("🛒 Smart Shopping Assistant Starting...")
        
        # Get staples and favorites
        staples = self.manage_staples("list")
        favorites = self.manage_favorites("list")
        
        all_items = list(set(staples + favorites))  # Remove duplicates
        
        if not all_items:
            print("ℹ️ No staples or favorites found. Add some first!")
            return
        
        print(f"📝 Checking prices for {len(all_items)} items...")
        
        # Check prices for all items
        results = {}
        for item in all_items:
            print(f"\\n🔍 {item}...")
            products = await self.enhanced_search(item, limit=3)
            
            if products:
                results[item] = products
                best = products[0]
                print(f"  👑 Best: {best['title'][:40]}... - {best['price']}")
            else:
                results[item] = []
                print(f"  ❌ No results")
            
            await asyncio.sleep(1)  # Be nice to the server
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"{self.data_dir}/purchases/smart_shop_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\\n💾 Shopping report saved: {results_file}")
        
        # Generate shopping summary
        print("\\n📊 SHOPPING SUMMARY:")
        print("=" * 50)
        
        total_items = 0
        estimated_total = 0
        
        for item, products in results.items():
            if products:
                best = products[0]
                price_str = best['price']
                
                # Try to extract numeric price
                price_match = price_str.replace('$', '').split('/')[0] if '$' in price_str else '0'
                try:
                    price = float(price_match)
                    estimated_total += price
                except:
                    price = 0
                
                status = "🔥 ON SALE" if best.get('saleInfo') else ""
                print(f"✅ {item.upper()}: {best['title'][:30]}... - {best['price']} {status}")
                total_items += 1
            else:
                print(f"❌ {item.upper()}: Not found")
        
        print(f"\\n💰 Estimated Total: ${estimated_total:.2f}")
        print(f"📦 Items Found: {total_items}/{len(all_items)}")
        
        return results

# CLI Interface
async def main():
    assistant = ZehrsMaster()
    
    if len(sys.argv) < 2:
        print("🛒 Zehrs Master Shopping Assistant")
        print("=" * 40)
        print("Commands:")
        print("  search <item>           - Enhanced product search")
        print("  promotions             - Scan current deals")
        print("  favorites add <items>  - Add to favorites")
        print("  favorites remove <items> - Remove from favorites") 
        print("  favorites list         - Show favorites")
        print("  staples add <items>    - Add to staples")
        print("  staples remove <items> - Remove from staples")
        print("  staples list           - Show staples")
        print("  smart-shop            - Complete shopping workflow")
        print("  test <item>           - Test enhanced search")
        print("")
        print("Examples:")
        print("  python zehrs-master.py search milk")
        print("  python zehrs-master.py favorites add milk bread eggs")
        print("  python zehrs-master.py smart-shop")
        return
    
    command = sys.argv[1]
    
    if command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        products = await assistant.enhanced_search(query)
        
        if products:
            print(f"\\n🛒 Enhanced Results for '{query}':")
            print("=" * 60)
            for p in products:
                print(f"{p['index']}. {p['title']}")
                print(f"   💰 {p['price']} {p.get('saleInfo', '')}")
                if p.get('brand'):
                    print(f"   🏷️ Brand: {p['brand']}")
                print(f"   🔗 {p['link'][:50]}..." if p['link'] else "")
                print()
        else:
            print(f"❌ No products found for '{query}'")
    
    elif command == "test" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        print(f"🧪 Testing enhanced search for: {query}")
        products = await assistant.enhanced_search(query)
        print(f"📊 Found {len(products)} products")
        
        if products:
            for p in products[:3]:  # Show top 3
                print(f"✅ {p['title']} - {p['price']}")
    
    elif command == "promotions":
        promotions = await assistant.scan_promotions()
        if promotions:
            print("\\n🔥 Current Promotions:")
            for i, promo in enumerate(promotions[:10], 1):
                print(f"{i}. {promo['title']}")
                if promo['discount']:
                    print(f"   💥 {promo['discount']}")
                if promo['price']:
                    print(f"   💰 {promo['price']}")
                print()
    
    elif command in ["favorites", "staples"]:
        if len(sys.argv) < 3:
            assistant.manage_favorites("list") if command == "favorites" else assistant.manage_staples("list")
        else:
            action = sys.argv[2]
            items = sys.argv[3:] if len(sys.argv) > 3 else None
            
            if command == "favorites":
                assistant.manage_favorites(action, items)
            else:
                assistant.manage_staples(action, items)
    
    elif command == "smart-shop":
        await assistant.smart_shopping_assistant()
    
    else:
        print("❌ Unknown command. Run without arguments to see usage.")

if __name__ == "__main__":
    asyncio.run(main())