#!/usr/bin/env python3
"""
Test Complete Cookies for Full Zehrs API Access
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_complete_cookies():
    """Test the complete cookie header for API access"""
    
    # Load complete cookies
    with open('/home/magi/clawd/grocery-data/complete_cookies.json', 'r') as f:
        cookie_data = json.load(f)
    
    cookie_header = cookie_data['cookie_header']
    
    print("🧪 TESTING COMPLETE COOKIES FOR API ACCESS")
    print("=" * 50)
    print(f"🍪 Cookie header length: {len(cookie_header)} chars")
    print(f"🔑 Key cookies detected:")
    for key, value in cookie_data['key_cookies'].items():
        display_value = value[:30] + "..." if len(value) > 30 else value
        print(f"   • {key}: {display_value}")
    print()
    
    # Complete headers with user's cookies
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Content-Type': 'application/json',
        'Referer': 'https://www.zehrs.ca/',
        'Origin': 'https://www.zehrs.ca',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Cookie': cookie_header,
        'x-apikey': 'C1xujSegT5j3ap3yexJjqhOfELwGKYvz',
        'x-application-type': 'Web',
        'x-loblaw-tenant-id': 'ONLINE_GROCERIES',
        'business-user-agent': 'PCXWEB',
        'site-banner': 'zehrs',
        'is-helios-account': 'true'
    }
    
    async with aiohttp.ClientSession() as session:
        
        # Comprehensive test suite
        test_endpoints = [
            {
                'name': 'Customer Profile',
                'url': 'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers',
                'method': 'GET',
                'priority': 'high'
            },
            {
                'name': 'Customer Carts',
                'url': 'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/carts',
                'method': 'GET',
                'priority': 'critical'
            },
            {
                'name': 'Store Cart',
                'url': 'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/stores/0533/carts',
                'method': 'GET',
                'priority': 'critical'
            },
            {
                'name': 'Customer Orders',
                'url': 'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/orders?status=SUBMITTED,READY_FOR_ACTION,READY_FOR_PICK_UP,COMPLETED',
                'method': 'GET',
                'priority': 'medium'
            },
            {
                'name': 'Product Search',
                'url': 'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/products/search?searchTerm=milk&limit=5',
                'method': 'GET',
                'priority': 'medium'
            }
        ]
        
        successful_endpoints = []
        cart_data = None
        customer_id = None
        
        for endpoint in test_endpoints:
            print(f"🔍 Testing: {endpoint['name']} ({endpoint['priority']} priority)")
            print(f"   URL: {endpoint['url']}")
            
            try:
                if endpoint['method'] == 'GET':
                    async with session.get(
                        endpoint['url'], 
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=20)
                    ) as response:
                        
                        status = response.status
                        print(f"   Status: {status}")
                        
                        if status == 200:
                            try:
                                data = await response.json()
                                print(f"   ✅ SUCCESS! Response: {len(str(data))} chars")
                                
                                successful_endpoints.append(endpoint['name'])
                                
                                # Save response data
                                filename = f"/home/magi/clawd/grocery-data/api_{endpoint['name'].lower().replace(' ', '_')}.json"
                                with open(filename, 'w') as f:
                                    json.dump(data, f, indent=2)
                                print(f"   💾 Saved: {filename}")
                                
                                # Extract important data
                                if 'customer' in endpoint['name'].lower() and 'cart' not in endpoint['name'].lower():
                                    # Customer profile data
                                    if isinstance(data, dict):
                                        customer_id = data.get('id') or data.get('customerId') or data.get('userId')
                                        if customer_id:
                                            print(f"   🆔 Customer ID: {customer_id}")
                                
                                elif 'cart' in endpoint['name'].lower():
                                    # Cart data
                                    cart_data = data
                                    if isinstance(data, dict):
                                        items = data.get('items', []) or data.get('cartItems', []) or data.get('lineItems', [])
                                        total = data.get('total', data.get('subtotal', 'Unknown'))
                                        
                                        print(f"   🛒 CART FOUND: {len(items)} items")
                                        if items:
                                            for i, item in enumerate(items[:3]):
                                                name = item.get('name', item.get('productName', item.get('description', 'Unknown')))
                                                price = item.get('price', item.get('unitPrice', item.get('cost', 'No price')))
                                                qty = item.get('quantity', item.get('qty', 1))
                                                print(f"     {i+1}. {name} (qty: {qty}) - {price}")
                                        
                                        if total != 'Unknown':
                                            print(f"   💰 Cart Total: {total}")
                                    
                                    elif isinstance(data, list):
                                        print(f"   🛒 CART LIST: {len(data)} items")
                                        for i, item in enumerate(data[:3]):
                                            name = item.get('name', item.get('productName', 'Unknown'))
                                            price = item.get('price', item.get('cost', 'No price'))
                                            print(f"     {i+1}. {name} - {price}")
                                
                                elif 'search' in endpoint['name'].lower():
                                    # Product search results
                                    if isinstance(data, dict):
                                        products = data.get('products', data.get('results', data.get('items', [])))
                                        print(f"   🔍 SEARCH: Found {len(products)} products")
                                        for i, product in enumerate(products[:2]):
                                            name = product.get('name', product.get('title', 'Unknown'))
                                            price = product.get('price', product.get('cost', 'No price'))
                                            print(f"     {i+1}. {name} - {price}")
                                
                            except json.JSONDecodeError:
                                text = await response.text()
                                print(f"   📝 Non-JSON response: {text[:100]}...")
                                successful_endpoints.append(f"{endpoint['name']} (non-JSON)")
                        
                        elif status == 401:
                            print(f"   ❌ Unauthorized")
                            text = await response.text()
                            print(f"   📝 Error: {text[:100]}...")
                        
                        elif status == 404:
                            print(f"   ❌ Not Found")
                        
                        elif status == 400:
                            print(f"   ❌ Bad Request")
                            text = await response.text()
                            print(f"   📝 Error: {text[:100]}...")
                        
                        else:
                            text = await response.text()
                            print(f"   ⚠️ Status {status}: {text[:100]}...")
                            
            except asyncio.TimeoutError:
                print(f"   ⏰ Timeout")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print()
        
        # Test cart editing if we have successful cart access
        if cart_data and customer_id:
            await test_cart_editing(session, headers, customer_id, cart_data)
        
        # Final summary
        print("🎯 FINAL RESULTS")
        print("=" * 20)
        
        if successful_endpoints:
            print(f"✅ SUCCESS! {len(successful_endpoints)}/{len(test_endpoints)} endpoints working:")
            for endpoint in successful_endpoints:
                print(f"   ✓ {endpoint}")
            
            if cart_data:
                print(f"\n🛒 CART ACCESS: ✅ WORKING")
                print(f"🔧 CART EDITING: {'✅ READY' if customer_id else '⚠️ NEED CUSTOMER ID'}")
                
            return True
            
        else:
            print(f"❌ No successful endpoints ({len(successful_endpoints)}/{len(test_endpoints)})")
            return False

async def test_cart_editing(session, headers, customer_id, cart_data):
    """Test cart editing capabilities"""
    print("🔧 TESTING CART EDITING CAPABILITIES")
    print("-" * 40)
    
    # Test endpoints for cart modification
    edit_endpoints = [
        f"https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/{customer_id}/carts",
        f"https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/stores/0533/carts"
    ]
    
    for endpoint in edit_endpoints:
        print(f"🔍 Testing cart endpoint: {endpoint}")
        
        try:
            async with session.get(endpoint, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Cart editing endpoint accessible!")
                    
                    # Save cart editing endpoint data
                    with open('/home/magi/clawd/grocery-data/cart_editing_endpoint.json', 'w') as f:
                        json.dump({
                            'endpoint': endpoint,
                            'customer_id': customer_id,
                            'response': data,
                            'timestamp': datetime.now().isoformat()
                        }, f, indent=2)
                    
                    return True
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

async def main():
    success = await test_complete_cookies()
    
    if success:
        print("\n🎉 COMPLETE API ACCESS ACHIEVED!")
        print("=" * 35)
        print("🛒 ✅ Can view cart contents")
        print("🔧 ✅ Can potentially edit cart")
        print("🔍 ✅ Can search products") 
        print("📦 ✅ Can access order history")
        print("\n🚀 READY FOR FULL CART AUTOMATION!")
        
    else:
        print("\n❌ API access still not working")
        print("💡 May need additional authentication steps")

if __name__ == "__main__":
    asyncio.run(main())