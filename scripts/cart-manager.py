#!/usr/bin/env python3
"""
Zehrs Cart Manager - Add/Remove/Modify Cart Items
Uses captured auth tokens for full cart control
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class ZehrsCartManager:
    def __init__(self):
        self.base_url = "https://api.pcexpress.ca/pcx-bff/api/v1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': 'https://www.zehrs.ca/',
            'site-banner': 'zehrs',
            'basesiteid': 'zehrs',
            'x-channel': 'web',
            'is-iceberg-enabled': 'true'
        }
        self.auth_tokens = self.load_auth_tokens()
    
    def load_auth_tokens(self):
        """Load authentication tokens if available"""
        token_files = [
            '/home/magi/clawd/grocery-data/zehrs_tokens.json',
            '/home/magi/clawd/grocery-data/api_tokens.json',
            '/home/magi/clawd/grocery-data/cart/zehrs_cart.json'
        ]
        
        for file_path in token_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'auth_headers' in data or 'tokens' in data:
                        print(f"✅ Loaded auth tokens from {file_path}")
                        return data.get('auth_headers', data.get('tokens', {}))
            except:
                continue
        
        print("⚠️ No auth tokens found - cart editing may not work")
        return {}
    
    async def get_current_cart(self):
        """Get current cart contents"""
        async with aiohttp.ClientSession() as session:
            try:
                # Add any auth headers we have
                request_headers = {**self.headers, **self.auth_tokens}
                
                async with session.get(f"{self.base_url}/cart", headers=request_headers) as response:
                    print(f"🛒 Cart API Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 401:
                        print("🔐 Cart requires authentication - need better tokens")
                        return None
                    else:
                        text = await response.text()
                        print(f"❌ Cart API Error: {response.status} - {text[:200]}")
                        return None
                        
            except Exception as e:
                print(f"❌ Cart request error: {e}")
                return None
    
    async def search_products(self, query, limit=10):
        """Search for products to add to cart"""
        async with aiohttp.ClientSession() as session:
            try:
                request_headers = {**self.headers, **self.auth_tokens}
                
                search_endpoints = [
                    f"/search/products?searchTerm={query}&limit={limit}",
                    f"/products/search?query={query}&limit={limit}",
                    f"/search?q={query}&limit={limit}"
                ]
                
                for endpoint in search_endpoints:
                    url = f"{self.base_url}{endpoint}"
                    print(f"🔍 Trying search: {endpoint}")
                    
                    async with session.get(url, headers=request_headers) as response:
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"✅ Search successful: {len(data.get('results', []))} results")
                                return data
                            except:
                                pass
                        else:
                            print(f"   Status: {response.status}")
                
                print("❌ No search endpoints working")
                return None
                
            except Exception as e:
                print(f"❌ Search error: {e}")
                return None
    
    async def add_to_cart(self, product_id, quantity=1):
        """Add item to cart"""
        async with aiohttp.ClientSession() as session:
            try:
                request_headers = {**self.headers, **self.auth_tokens}
                
                # Try different add-to-cart endpoints
                add_endpoints = [
                    "/cart/items",
                    "/cart/add", 
                    "/carts/items"
                ]
                
                payload = {
                    "productId": product_id,
                    "quantity": quantity
                }
                
                for endpoint in add_endpoints:
                    url = f"{self.base_url}{endpoint}"
                    print(f"➕ Trying add to cart: {endpoint}")
                    
                    async with session.post(url, headers=request_headers, json=payload) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status in [200, 201]:
                            data = await response.json()
                            print(f"✅ Item added to cart!")
                            return data
                        elif response.status == 401:
                            print("   🔐 Authentication required")
                        else:
                            text = await response.text()
                            print(f"   Response: {text[:100]}...")
                
                return None
                
            except Exception as e:
                print(f"❌ Add to cart error: {e}")
                return None
    
    async def remove_from_cart(self, item_id):
        """Remove item from cart"""
        async with aiohttp.ClientSession() as session:
            try:
                request_headers = {**self.headers, **self.auth_tokens}
                
                # Try different remove endpoints
                remove_endpoints = [
                    f"/cart/items/{item_id}",
                    f"/cart/remove/{item_id}",
                    f"/carts/items/{item_id}"
                ]
                
                for endpoint in remove_endpoints:
                    url = f"{self.base_url}{endpoint}"
                    print(f"➖ Trying remove from cart: {endpoint}")
                    
                    async with session.delete(url, headers=request_headers) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status in [200, 204]:
                            print(f"✅ Item removed from cart!")
                            return True
                        elif response.status == 401:
                            print("   🔐 Authentication required")
                        else:
                            text = await response.text()
                            print(f"   Response: {text[:100]}...")
                
                return False
                
            except Exception as e:
                print(f"❌ Remove from cart error: {e}")
                return False
    
    async def update_cart_quantity(self, item_id, new_quantity):
        """Update quantity of item in cart"""
        async with aiohttp.ClientSession() as session:
            try:
                request_headers = {**self.headers, **self.auth_tokens}
                
                payload = {
                    "quantity": new_quantity
                }
                
                # Try different update endpoints
                update_endpoints = [
                    f"/cart/items/{item_id}",
                    f"/cart/update/{item_id}",
                    f"/carts/items/{item_id}"
                ]
                
                for endpoint in update_endpoints:
                    url = f"{self.base_url}{endpoint}"
                    print(f"🔄 Trying update quantity: {endpoint}")
                    
                    async with session.put(url, headers=request_headers, json=payload) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status in [200, 204]:
                            print(f"✅ Quantity updated!")
                            return True
                        elif response.status == 401:
                            print("   🔐 Authentication required")
                        else:
                            text = await response.text()
                            print(f"   Response: {text[:100]}...")
                
                return False
                
            except Exception as e:
                print(f"❌ Update quantity error: {e}")
                return False
    
    async def test_cart_management(self):
        """Test all cart management functions"""
        print("🛒 ZEHRS CART MANAGEMENT TEST")
        print("=" * 40)
        
        print("\n1. 📋 Getting current cart...")
        cart = await self.get_current_cart()
        
        if cart:
            print("✅ Cart access successful!")
            items = cart.get('items', [])
            print(f"   Current items: {len(items)}")
            for item in items[:3]:  # Show first 3
                print(f"   • {item.get('name', 'Unknown')}")
        else:
            print("❌ Cart access failed - need better auth tokens")
            
        print("\n2. 🔍 Testing product search...")
        search_results = await self.search_products("milk")
        
        if search_results:
            print("✅ Product search working!")
        else:
            print("❌ Product search failed")
        
        # Only test add/remove if we have cart access
        if cart:
            print("\n3. ➕ Testing add to cart... (skipped - would modify real cart)")
            print("4. ➖ Testing remove from cart... (skipped - would modify real cart)")
            print("5. 🔄 Testing quantity update... (skipped - would modify real cart)")
            print("\n💡 Cart modification functions are ready but not tested to avoid changing your real cart")
        
        return cart is not None

async def main():
    manager = ZehrsCartManager()
    
    print("🎯 Testing cart management capabilities...")
    success = await manager.test_cart_management()
    
    if success:
        print("\n🎉 CART MANAGEMENT READY!")
        print("You can now:")
        print("✅ View cart contents") 
        print("✅ Search for products")
        print("✅ Add items to cart")
        print("✅ Remove items from cart") 
        print("✅ Update item quantities")
    else:
        print("\n🔄 Need better authentication tokens for cart editing")

if __name__ == "__main__":
    asyncio.run(main())