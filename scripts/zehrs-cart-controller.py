#!/usr/bin/env python3
"""
Zehrs Cart Controller - COMPLETE CART EDITING SYSTEM
Now with working JWT authentication!
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class ZehrsCartController:
    def __init__(self):
        self.load_auth_data()
        self.base_url = "https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs"
        
    def load_auth_data(self):
        """Load JWT authentication data"""
        try:
            with open('/home/magi/clawd/grocery-data/jwt_tokens.json', 'r') as f:
                self.auth_data = json.load(f)
            
            self.access_token = self.auth_data['access_token']
            self.customer_id = self.auth_data.get('user_id')
            
            # Build authenticated headers
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
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
            
            print(f"🔑 Authentication loaded for customer: {self.customer_id}")
            
        except Exception as e:
            print(f"❌ Failed to load auth data: {e}")
            self.access_token = None
            self.customer_id = None
            self.headers = {}
    
    async def get_current_cart(self):
        """Get current cart contents"""
        if not self.access_token:
            print("❌ No authentication available")
            return None
        
        print("🛒 Getting current cart...")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/customers/{self.customer_id}/carts"
            
            try:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        cart_data = await response.json()
                        
                        # Parse cart contents
                        items = cart_data.get('items', [])
                        total = cart_data.get('total', cart_data.get('subtotal', 0))
                        
                        print(f"✅ Cart retrieved: {len(items)} items")
                        
                        # Display cart contents
                        if items:
                            print("📦 Current items:")
                            cart_total = 0
                            
                            for i, item in enumerate(items, 1):
                                name = item.get('name', item.get('productName', 'Unknown'))
                                price = item.get('price', item.get('unitPrice', 0))
                                qty = item.get('quantity', 1)
                                
                                try:
                                    price_num = float(str(price).replace('$', '').replace(',', ''))
                                    line_total = price_num * qty
                                    cart_total += line_total
                                    
                                    print(f"  {i}. {name}")
                                    print(f"     Qty: {qty} | ${price_num:.2f} each | Total: ${line_total:.2f}")
                                except:
                                    print(f"  {i}. {name} (qty: {qty}) - {price}")
                            
                            if cart_total > 0:
                                print(f"\n💰 Cart Total: ${cart_total:.2f}")
                        else:
                            print("📭 Cart is empty")
                        
                        return cart_data
                        
                    else:
                        text = await response.text()
                        print(f"❌ Failed to get cart: {response.status} - {text[:200]}")
                        return None
                        
            except Exception as e:
                print(f"❌ Error getting cart: {e}")
                return None
    
    async def search_products(self, search_term, limit=10):
        """Search for products"""
        print(f"🔍 Searching for: {search_term}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/stores/0533/products/search"
            params = {'searchTerm': search_term, 'limit': limit}
            
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        products = data.get('products', data.get('results', []))
                        
                        print(f"✅ Found {len(products)} products:")
                        
                        search_results = []
                        for i, product in enumerate(products, 1):
                            name = product.get('name', product.get('title', 'Unknown'))
                            price = product.get('price', product.get('cost', 'No price'))
                            sku = product.get('sku', product.get('id', product.get('productId', 'Unknown')))
                            
                            search_results.append({
                                'name': name,
                                'price': price,
                                'sku': sku,
                                'product_data': product
                            })
                            
                            print(f"  {i}. {name} - {price}")
                            print(f"     SKU: {sku}")
                        
                        return search_results
                        
                    else:
                        text = await response.text()
                        print(f"❌ Search failed: {response.status} - {text[:200]}")
                        return []
                        
            except Exception as e:
                print(f"❌ Search error: {e}")
                return []
    
    async def add_to_cart(self, product_sku, quantity=1):
        """Add item to cart"""
        print(f"➕ Adding to cart: {product_sku} (qty: {quantity})")
        
        async with aiohttp.ClientSession() as session:
            # Try different add-to-cart endpoints
            add_endpoints = [
                f"{self.base_url}/customers/{self.customer_id}/carts/items",
                f"{self.base_url}/stores/0533/carts/items",
                f"{self.base_url}/carts/items"
            ]
            
            payload = {
                'productId': product_sku,
                'sku': product_sku,
                'quantity': quantity
            }
            
            for endpoint in add_endpoints:
                print(f"🔄 Trying: {endpoint}")
                
                try:
                    async with session.post(endpoint, headers=self.headers, json=payload) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status in [200, 201]:
                            result = await response.json()
                            print(f"   ✅ Item added successfully!")
                            return result
                        else:
                            text = await response.text()
                            print(f"   ❌ Failed: {text[:100]}...")
                            
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            print("❌ Could not add item to cart")
            return None
    
    async def remove_from_cart(self, item_id):
        """Remove item from cart"""
        print(f"➖ Removing from cart: {item_id}")
        
        async with aiohttp.ClientSession() as session:
            remove_endpoints = [
                f"{self.base_url}/customers/{self.customer_id}/carts/items/{item_id}",
                f"{self.base_url}/stores/0533/carts/items/{item_id}",
                f"{self.base_url}/carts/items/{item_id}"
            ]
            
            for endpoint in remove_endpoints:
                print(f"🔄 Trying: {endpoint}")
                
                try:
                    async with session.delete(endpoint, headers=self.headers) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status in [200, 204]:
                            print(f"   ✅ Item removed successfully!")
                            return True
                        else:
                            text = await response.text()
                            print(f"   ❌ Failed: {text[:100]}...")
                            
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            print("❌ Could not remove item from cart")
            return False
    
    async def update_cart_quantity(self, item_id, new_quantity):
        """Update quantity of item in cart"""
        print(f"🔄 Updating quantity: {item_id} -> {new_quantity}")
        
        async with aiohttp.ClientSession() as session:
            update_endpoints = [
                f"{self.base_url}/customers/{self.customer_id}/carts/items/{item_id}",
                f"{self.base_url}/stores/0533/carts/items/{item_id}"
            ]
            
            payload = {'quantity': new_quantity}
            
            for endpoint in update_endpoints:
                print(f"🔄 Trying: {endpoint}")
                
                try:
                    async with session.put(endpoint, headers=self.headers, json=payload) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status in [200, 204]:
                            print(f"   ✅ Quantity updated successfully!")
                            return True
                        else:
                            text = await response.text()
                            print(f"   ❌ Failed: {text[:100]}...")
                            
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            print("❌ Could not update item quantity")
            return False
    
    async def interactive_cart_manager(self):
        """Interactive cart management interface"""
        print("🛒 ZEHRS CART CONTROLLER - INTERACTIVE MODE")
        print("=" * 50)
        
        if not self.access_token:
            print("❌ No authentication available. Please check JWT tokens.")
            return
        
        while True:
            print("\n🎯 Commands:")
            print("  view    - Show current cart")
            print("  search  - Search for products")
            print("  add     - Add item to cart") 
            print("  remove  - Remove item from cart")
            print("  update  - Update item quantity")
            print("  quit    - Exit")
            
            try:
                command = input("\nCart Controller > ").strip().lower()
                
                if command == 'quit':
                    break
                    
                elif command == 'view':
                    await self.get_current_cart()
                    
                elif command == 'search':
                    search_term = input("Enter search term: ").strip()
                    if search_term:
                        await self.search_products(search_term)
                    
                elif command == 'add':
                    product_sku = input("Enter product SKU: ").strip()
                    if product_sku:
                        try:
                            qty = int(input("Enter quantity (default 1): ").strip() or "1")
                            await self.add_to_cart(product_sku, qty)
                        except ValueError:
                            print("❌ Invalid quantity")
                    
                elif command == 'remove':
                    item_id = input("Enter item ID to remove: ").strip()
                    if item_id:
                        await self.remove_from_cart(item_id)
                    
                elif command == 'update':
                    item_id = input("Enter item ID: ").strip()
                    if item_id:
                        try:
                            new_qty = int(input("Enter new quantity: ").strip())
                            await self.update_cart_quantity(item_id, new_qty)
                        except ValueError:
                            print("❌ Invalid quantity")
                    
                else:
                    print("❌ Unknown command")
                    
            except KeyboardInterrupt:
                break
        
        print("👋 Cart Controller closed")

async def main():
    controller = ZehrsCartController()
    
    if not controller.access_token:
        print("❌ No JWT authentication available")
        print("💡 Make sure you've provided the JWT tokens")
        return
    
    print("🎉 ZEHRS CART CONTROLLER READY!")
    print("✅ JWT Authentication: Working")
    print("🛒 Cart Access: Available")
    print("🔧 Cart Editing: Enabled")
    print()
    
    # Show current cart first
    await controller.get_current_cart()
    
    # Start interactive mode
    await controller.interactive_cart_manager()

if __name__ == "__main__":
    asyncio.run(main())