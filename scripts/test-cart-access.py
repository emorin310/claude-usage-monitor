#!/usr/bin/env python3
"""
Test Cart Access with Extracted Headers
"""

import asyncio
import aiohttp
import json

async def test_zehrs_cart_access():
    """Test cart access with extracted authentication headers"""
    
    # Load the working headers
    with open('/home/magi/clawd/grocery-data/working_auth_headers.json', 'r') as f:
        headers = json.load(f)
    
    print("🛒 TESTING CART ACCESS WITH EXTRACTED HEADERS")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Try cart API
        cart_endpoints = [
            "https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/carts",
            "https://api.pcexpress.ca/pcx-bff/api/v1/cart",
            "https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/cart"
        ]
        
        for endpoint in cart_endpoints:
            print(f"\n🔍 Testing: {endpoint}")
            try:
                async with session.get(endpoint, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"   ✅ SUCCESS! Cart data received: {len(str(data))} chars")
                            
                            # Save cart data
                            with open('/home/magi/clawd/grocery-data/api_cart_data.json', 'w') as f:
                                json.dump(data, f, indent=2)
                            
                            print(f"   💾 Cart data saved to api_cart_data.json")
                            return True
                            
                        except json.JSONDecodeError:
                            text = await response.text()
                            print(f"   📝 Non-JSON response: {text[:100]}...")
                    
                    elif response.status == 401:
                        print(f"   ❌ Unauthorized - headers may not be sufficient")
                    elif response.status == 404:
                        print(f"   ❌ Endpoint not found")
                    else:
                        text = await response.text()
                        print(f"   ⚠️ Status {response.status}: {text[:100]}...")
                        
            except asyncio.TimeoutError:
                print(f"   ⏰ Timeout")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test 2: Try customer API (which we know works)
        print(f"\n🧑 Testing customer API (known working)...")
        customer_url = "https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers?syncRippleMembership=true"
        
        try:
            async with session.get(customer_url, headers=headers) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Customer API works! Data: {len(str(data))} chars")
                    
                    # Check if we have customer ID for cart access
                    customer_id = data.get('id') or data.get('customerId') or data.get('userId')
                    if customer_id:
                        print(f"   🆔 Customer ID found: {customer_id}")
                        
                        # Try customer-specific cart endpoint
                        customer_cart_url = f"https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/{customer_id}/carts"
                        print(f"\n🛒 Testing customer-specific cart: {customer_cart_url}")
                        
                        async with session.get(customer_cart_url, headers=headers) as cart_response:
                            print(f"   Status: {cart_response.status}")
                            if cart_response.status == 200:
                                cart_data = await cart_response.json()
                                print(f"   🎉 CUSTOMER CART ACCESS SUCCESSFUL!")
                                
                                with open('/home/magi/clawd/grocery-data/api_customer_cart.json', 'w') as f:
                                    json.dump(cart_data, f, indent=2)
                                
                                return True
                
        except Exception as e:
            print(f"   ❌ Customer API error: {e}")
        
        # Test 3: Try search API 
        print(f"\n🔍 Testing product search API...")
        search_url = "https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/products/search"
        search_params = {"searchTerm": "milk", "limit": 5}
        
        try:
            async with session.get(search_url, headers=headers, params=search_params) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Product search works! Found products")
                    
                    # Check if we have products
                    products = data.get('products', []) or data.get('results', [])
                    if products:
                        print(f"   📦 Found {len(products)} products")
                        for i, product in enumerate(products[:3]):
                            name = product.get('name', product.get('title', 'Unknown'))
                            price = product.get('price', product.get('cost', 'No price'))
                            print(f"     {i+1}. {name} - {price}")
                
        except Exception as e:
            print(f"   ❌ Search API error: {e}")
        
        return False

async def main():
    success = await test_zehrs_cart_access()
    
    if success:
        print("\n🎉 CART ACCESS ACHIEVED!")
        print("✅ Authentication headers are working")
        print("🛒 Can now view and potentially edit cart")
        print("🎯 Next: Test add/remove cart functions")
    else:
        print("\n🔄 Cart access not yet working")
        print("💡 May need additional authentication steps")

if __name__ == "__main__":
    asyncio.run(main())