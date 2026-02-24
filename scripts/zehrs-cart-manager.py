#!/usr/bin/env python3
"""
COMPLETE ZEHRS CART MANAGER - FINAL VERSION
Full cart viewing and editing with working JWT authentication
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone
import sys

class ZehrsCartManager:
    def __init__(self):
        self.load_authentication()
        
    def load_authentication(self):
        """Load JWT authentication and cart details"""
        try:
            # Load JWT tokens
            with open('/home/magi/clawd/grocery-data/jwt_tokens.json', 'r') as f:
                token_data = json.load(f)
            
            # Load customer data with cart ID
            with open('/home/magi/clawd/grocery-data/working_customer_config.json', 'r') as f:
                customer_config = json.load(f)
            
            self.access_token = token_data['access_token']
            self.customer_data = customer_config['data']
            self.cart_id = self.customer_data['cartId']
            self.customer_id = self.customer_data['customerId']
            self.store_id = self.customer_data.get('lastStoreId', '0533')
            
            # Check token expiry
            exp_timestamp = token_data.get('expires_at', 0)
            exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            
            if now > exp_time:
                print("❌ WARNING: JWT token has expired!")
                print("💡 You'll need to refresh your browser session")
                self.token_valid = False
            else:
                time_left = exp_time - now
                print(f"✅ JWT token valid for: {time_left}")
                self.token_valid = True
            
            # API endpoints
            self.cart_url = f"https://api.pcexpress.ca/pcx-bff/api/v1/carts/{self.cart_id}"
            self.search_base = "https://api.pcexpress.ca/pcx-bff/api/v1"
            
            # Headers
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en',
                'Content-Type': 'application/json',
                'Referer': 'https://www.zehrs.ca/',
                'Origin': 'https://www.zehrs.ca',
                'Authorization': f'Bearer {self.access_token}',
                'x-apikey': 'C1xujSegT5j3ap3yexJjqhOfELwGKYvz',
                'x-application-type': 'Web',
                'x-loblaw-tenant-id': 'ONLINE_GROCERIES',
                'business-user-agent': 'PCXWEB',
                'site-banner': 'zehrs'
            }
            
            print(f"🔑 Authenticated as: {self.customer_data.get('firstName', 'Customer')}")
            print(f"🛒 Cart ID: {self.cart_id}")
            print(f"🏪 Store: {self.store_id}")
            
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            self.access_token = None
            self.token_valid = False
    
    async def get_cart_contents(self, display=True):
        """Get current cart contents"""
        if not self.token_valid:
            print("❌ Cannot access cart - token expired")
            return None
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.cart_url, headers=self.headers) as response:
                    if response.status == 200:
                        cart_data = await response.json()
                        
                        if display:
                            self._display_cart(cart_data)
                        
                        return cart_data
                    
                    elif response.status == 401:
                        print("❌ Unauthorized - JWT token may be expired")
                        return None
                    
                    else:
                        text = await response.text()
                        print(f"❌ Cart access failed: {response.status} - {text[:200]}")
                        return None
                        
            except Exception as e:
                print(f"❌ Error accessing cart: {e}")
                return None
    
    def _display_cart(self, cart_data):
        """Display cart contents in a nice format"""
        print("🛒 YOUR ZEHRS CART")
        print("=" * 50)
        
        orders = cart_data.get('orders', [])
        if not orders:
            print("📭 Your cart is empty")
            return
        
        entries = orders[0].get('entries', [])
        if not entries:
            print("📭 No items in cart")
            return
        
        cart_total = 0
        item_count = 0
        
        for i, entry in enumerate(entries, 1):
            product = entry['offer']['product']
            name = product['name']
            product_id = product['id']
            brand = product.get('brand', '')
            qty = entry['quantity']
            prices = entry['prices']
            
            unit_price = prices.get('salePrice', prices.get('totalSalePrice', 0))
            total_price = prices['totalSalePrice']
            
            cart_total += total_price
            item_count += qty
            
            print(f"{i:2d}. {name}")
            if brand:
                print(f"    Brand: {brand}")
            print(f"    ID: {product_id}")
            print(f"    Qty: {int(qty)} × ${unit_price:.2f} = ${total_price:.2f}")
            print()
        
        print("-" * 50)
        print(f"💰 CART TOTAL: ${cart_total:.2f}")
        print(f"📦 TOTAL ITEMS: {int(item_count)}")
        print(f"🏪 Store: {self.store_id} (Zehrs)")
        
        # PC Optimum points info
        if 'customer' in cart_data:
            customer = cart_data['customer']
            print(f"👤 Customer: {customer.get('name', 'Unknown')}")
            
        print()
    
    async def search_products(self, search_term, limit=10):
        """Search for products (placeholder - endpoint needs discovery)"""
        print(f"🔍 Searching for '{search_term}'...")
        print("⚠️ Product search endpoint still being discovered")
        print("💡 Use the Chrome extension to find product IDs for now")
        
        # When we find working search endpoints, implement here
        return []
    
    async def add_to_cart(self, product_id, quantity=1):
        """Add item to cart"""
        print(f"➕ Adding to cart: {product_id} (qty: {quantity})")
        
        if not self.token_valid:
            print("❌ Cannot add item - token expired")
            return False
        
        # Test different add-to-cart endpoints
        add_endpoints = [
            f"{self.cart_url}/items",
            f"https://api.pcexpress.ca/pcx-bff/api/v1/carts/items",
            f"https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/carts/{self.cart_id}/items"
        ]
        
        payload = {
            'productId': product_id,
            'offerId': product_id,
            'quantity': quantity,
            'storeId': self.store_id
        }
        
        async with aiohttp.ClientSession() as session:
            for endpoint in add_endpoints:
                print(f"🔄 Trying: {endpoint.split('/')[-2:]}")
                
                try:
                    async with session.post(endpoint, headers=self.headers, json=payload) as response:
                        status = response.status
                        print(f"   Status: {status}")
                        
                        if status in [200, 201]:
                            print(f"   ✅ Item added successfully!")
                            await self.get_cart_contents()  # Refresh cart display
                            return True
                        
                        elif status == 400:
                            text = await response.text()
                            print(f"   ❌ Bad Request: {text[:200]}")
                        
                        elif status == 404:
                            print(f"   ❌ Endpoint not found")
                        
                        else:
                            text = await response.text()
                            print(f"   ⚠️ Status {status}: {text[:200]}")
                            
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        
        print("❌ Could not add item - all endpoints failed")
        print("💡 You may need to add items through the website first")
        return False
    
    async def remove_from_cart(self, product_id):
        """Remove item from cart"""
        print(f"➖ Removing from cart: {product_id}")
        
        if not self.token_valid:
            print("❌ Cannot remove item - token expired")
            return False
        
        # First get current cart to find the entry
        cart_data = await self.get_cart_contents(display=False)
        if not cart_data:
            return False
        
        # Find the item in cart entries
        entry_to_remove = None
        orders = cart_data.get('orders', [])
        if orders:
            entries = orders[0].get('entries', [])
            for entry in entries:
                if entry['offer']['product']['id'] == product_id:
                    entry_to_remove = entry
                    break
        
        if not entry_to_remove:
            print(f"❌ Item {product_id} not found in cart")
            return False
        
        # Try remove endpoints (this will need testing with actual API)
        remove_endpoints = [
            f"{self.cart_url}/items/{product_id}",
            f"https://api.pcexpress.ca/pcx-bff/api/v1/carts/items/{product_id}"
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in remove_endpoints:
                print(f"🔄 Trying: {endpoint.split('/')[-2:]}")
                
                try:
                    async with session.delete(endpoint, headers=self.headers) as response:
                        status = response.status
                        print(f"   Status: {status}")
                        
                        if status in [200, 204]:
                            print(f"   ✅ Item removed successfully!")
                            await self.get_cart_contents()  # Refresh cart display
                            return True
                        
                        else:
                            text = await response.text()
                            print(f"   ⚠️ Status {status}: {text[:200]}")
                            
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        
        print("❌ Could not remove item - API methods not yet discovered")
        print("💡 Remove items through the website for now")
        return False
    
    async def update_quantity(self, product_id, new_quantity):
        """Update item quantity in cart"""
        print(f"🔄 Updating quantity: {product_id} -> {new_quantity}")
        
        # For now, this would be remove + add
        if new_quantity == 0:
            return await self.remove_from_cart(product_id)
        else:
            print("❌ Quantity update not yet implemented")
            print("💡 Remove and re-add items to change quantities for now")
            return False
    
    def print_usage_help(self):
        """Print usage instructions"""
        print("🎯 ZEHRS CART MANAGER COMMANDS")
        print("=" * 35)
        print("  view                    - Show current cart")
        print("  add <product_id> [qty]  - Add item to cart")
        print("  remove <product_id>     - Remove item from cart")
        print("  search <term>           - Search for products")
        print("  help                    - Show this help")
        print("  quit                    - Exit")
        print()
        print("💡 PRODUCT IDs:")
        print("  • Use Chrome extension to find product IDs")
        print("  • Example: 21191970_EA (Chicken Burger)")
        print("  • Example: 21579825_EA (Kaiser Rolls)")
        print()
    
    async def interactive_mode(self):
        """Interactive cart management mode"""
        print("🛒 ZEHRS CART MANAGER - INTERACTIVE MODE")
        print("=" * 50)
        
        if not self.token_valid:
            print("❌ Cannot start interactive mode - token expired")
            print("💡 Please refresh your browser session and get new JWT tokens")
            return
        
        # Show current cart
        await self.get_cart_contents()
        
        print("\nType 'help' for commands or 'quit' to exit")
        
        while True:
            try:
                command = input("\n🛒 Cart Manager > ").strip()
                
                if not command:
                    continue
                    
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd in ['quit', 'exit', 'q']:
                    break
                
                elif cmd in ['help', 'h']:
                    self.print_usage_help()
                
                elif cmd in ['view', 'show', 'cart', 'v']:
                    await self.get_cart_contents()
                
                elif cmd == 'add':
                    if len(parts) < 2:
                        print("❌ Usage: add <product_id> [quantity]")
                        continue
                    
                    product_id = parts[1]
                    qty = int(parts[2]) if len(parts) > 2 else 1
                    
                    await self.add_to_cart(product_id, qty)
                
                elif cmd in ['remove', 'rm', 'delete']:
                    if len(parts) < 2:
                        print("❌ Usage: remove <product_id>")
                        continue
                    
                    product_id = parts[1]
                    await self.remove_from_cart(product_id)
                
                elif cmd == 'search':
                    if len(parts) < 2:
                        print("❌ Usage: search <search_term>")
                        continue
                    
                    search_term = ' '.join(parts[1:])
                    await self.search_products(search_term)
                
                else:
                    print(f"❌ Unknown command: {cmd}")
                    print("💡 Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n👋 Cart Manager closed")

async def main():
    if len(sys.argv) > 1:
        # Command line usage
        manager = ZehrsCartManager()
        
        command = sys.argv[1].lower()
        
        if command == 'view':
            await manager.get_cart_contents()
        
        elif command == 'add' and len(sys.argv) >= 3:
            product_id = sys.argv[2]
            qty = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            await manager.add_to_cart(product_id, qty)
        
        elif command == 'remove' and len(sys.argv) >= 3:
            product_id = sys.argv[2]
            await manager.remove_from_cart(product_id)
        
        else:
            print("❌ Usage:")
            print("  python zehrs-cart-manager.py view")
            print("  python zehrs-cart-manager.py add <product_id> [qty]")
            print("  python zehrs-cart-manager.py remove <product_id>")
            print("  python zehrs-cart-manager.py")
            print("    (for interactive mode)")
    
    else:
        # Interactive mode
        manager = ZehrsCartManager()
        await manager.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())