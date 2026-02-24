#!/usr/bin/env python3
"""
Test Cart Endpoints Using Specific Cart ID and Customer ID
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_cart_with_specific_ids():
    """Test cart endpoints using the cart ID from customer profile"""
    
    # Load the working customer config
    with open('/home/magi/clawd/grocery-data/working_customer_config.json', 'r') as f:
        customer_config = json.load(f)
    
    customer_data = customer_config['data']
    cart_id = customer_data.get('cartId')
    customer_id = customer_data.get('customerId')
    store_id = customer_data.get('lastStoreId', '0533')
    
    print("🛒 TESTING CART WITH SPECIFIC IDS")
    print("=" * 40)
    print(f"🆔 Cart ID: {cart_id}")
    print(f"👤 Customer ID: {customer_id}")  
    print(f"🏪 Store ID: {store_id}")
    print()
    
    # Load working auth headers
    with open('/home/magi/clawd/grocery-data/jwt_tokens.json', 'r') as f:
        token_data = json.load(f)
    
    access_token = token_data['access_token']
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        'Content-Type': 'application/json',
        'Referer': 'https://www.zehrs.ca/',
        'Origin': 'https://www.zehrs.ca',
        'Authorization': f'Bearer {access_token}',
        'x-apikey': 'C1xujSegT5j3ap3yexJjqhOfELwGKYvz',
        'x-application-type': 'Web',
        'x-loblaw-tenant-id': 'ONLINE_GROCERIES',
        'business-user-agent': 'PCXWEB',
        'site-banner': 'zehrs'
    }
    
    # Cart endpoints using specific IDs
    cart_endpoint_tests = [
        {
            'name': 'Cart by Cart ID',
            'url': f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/carts/{cart_id}'
        },
        {
            'name': 'Cart by Customer ID + Store',
            'url': f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/{customer_id}/stores/{store_id}/carts'
        },
        {
            'name': 'Store Cart by Cart ID',
            'url': f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/stores/{store_id}/carts/{cart_id}'
        },
        {
            'name': 'Direct Cart Access',
            'url': f'https://api.pcexpress.ca/pcx-bff/api/v1/carts/{cart_id}'
        },
        {
            'name': 'Ecommerce Cart Direct',
            'url': f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/carts/{cart_id}'
        },
        {
            'name': 'Customer Cart Items',
            'url': f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/{customer_id}/carts/{cart_id}/items'
        },
        {
            'name': 'Store Cart Items',  
            'url': f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/stores/{store_id}/carts/{cart_id}/items'
        },
        {
            'name': 'Cart Summary',
            'url': f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/carts/{cart_id}/summary'
        },
        {
            'name': 'Customer Cart Summary',
            'url': f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/{customer_id}/carts/summary'
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        working_cart_endpoints = []
        
        for test in cart_endpoint_tests:
            print(f"🔍 Testing: {test['name']}")
            print(f"   URL: {test['url']}")
            
            try:
                async with session.get(
                    test['url'],
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    status = response.status
                    print(f"   Status: {status}")
                    
                    if status == 200:
                        try:
                            data = await response.json()
                            print(f"   ✅ SUCCESS! Cart data: {len(str(data))} chars")
                            
                            working_cart_endpoints.append({
                                'name': test['name'],
                                'url': test['url'],
                                'data': data
                            })
                            
                            # Save cart data
                            filename = f"/home/magi/clawd/grocery-data/cart_{test['name'].lower().replace(' ', '_')}.json"
                            with open(filename, 'w') as f:
                                json.dump(data, f, indent=2)
                            print(f"   💾 Saved: {filename}")
                            
                            # Analyze cart contents
                            await analyze_cart_data(data, test['name'])
                            
                        except json.JSONDecodeError:
                            text = await response.text()
                            print(f"   📝 Non-JSON: {text[:150]}...")
                    
                    elif status == 404:
                        print(f"   ❌ Not Found")
                    elif status == 401:
                        print(f"   ❌ Unauthorized")
                    elif status == 400:
                        text = await response.text()
                        print(f"   ❌ Bad Request: {text[:100]}...")
                    else:
                        text = await response.text()
                        print(f"   ⚠️ Status {status}: {text[:150]}...")
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print()
        
        # Test product search endpoints with store ID
        await test_product_search_with_store(session, headers, store_id)
        
        # Summary
        print("🎯 CART ENDPOINT TEST RESULTS")
        print("=" * 35)
        
        if working_cart_endpoints:
            print(f"🎉 SUCCESS! Found {len(working_cart_endpoints)} working cart endpoints:")
            
            for endpoint in working_cart_endpoints:
                print(f"   ✅ {endpoint['name']}: {endpoint['url']}")
            
            # Save all working endpoints
            with open('/home/magi/clawd/grocery-data/working_cart_endpoints.json', 'w') as f:
                json.dump(working_cart_endpoints, f, indent=2)
            print(f"\n💾 All working cart endpoints saved!")
            
            # Test cart modification on working endpoints
            await test_cart_modification(session, headers, working_cart_endpoints[0])
            
        else:
            print(f"❌ No cart endpoints working ({len(working_cart_endpoints)}/{len(cart_endpoint_tests)})")
            print("💡 Cart may be empty or using different API structure")
        
        return len(working_cart_endpoints) > 0

async def analyze_cart_data(data, endpoint_name):
    """Analyze and display cart contents"""
    print(f"   📊 Analyzing cart data from {endpoint_name}:")
    
    # Different ways cart data might be structured
    items = []
    total = None
    
    if isinstance(data, dict):
        # Common cart data locations
        items = (data.get('items') or 
                data.get('cartItems') or 
                data.get('lineItems') or 
                data.get('products') or [])
        
        total = (data.get('total') or 
                data.get('subtotal') or 
                data.get('grandTotal') or 
                data.get('amount'))
        
        # Check for nested cart data
        if not items and 'cart' in data:
            cart_data = data['cart']
            items = (cart_data.get('items') or 
                    cart_data.get('cartItems') or [])
            total = cart_data.get('total')
    
    elif isinstance(data, list):
        items = data
    
    if items:
        print(f"   🛒 CART CONTAINS: {len(items)} items")
        cart_value = 0
        
        for i, item in enumerate(items[:5]):  # Show first 5 items
            name = (item.get('name') or 
                   item.get('productName') or 
                   item.get('description') or 
                   item.get('title') or 'Unknown Item')
            
            price = (item.get('price') or 
                    item.get('unitPrice') or 
                    item.get('cost') or 
                    item.get('linePrice') or 0)
            
            qty = (item.get('quantity') or 
                  item.get('qty') or 1)
            
            try:
                if isinstance(price, str):
                    price_num = float(price.replace('$', '').replace(',', ''))
                else:
                    price_num = float(price)
                
                line_total = price_num * qty
                cart_value += line_total
                
                print(f"     {i+1}. {name}")
                print(f"        Qty: {qty} | ${price_num:.2f} | Line: ${line_total:.2f}")
                
            except (ValueError, TypeError):
                print(f"     {i+1}. {name} (qty: {qty}) - {price}")
        
        if len(items) > 5:
            print(f"     ... and {len(items) - 5} more items")
        
        if cart_value > 0:
            print(f"   💰 Calculated Cart Total: ${cart_value:.2f}")
        elif total:
            print(f"   💰 Cart Total: {total}")
    
    else:
        print(f"   📭 Cart appears empty or different structure")
        print(f"   🔍 Data keys: {list(data.keys()) if isinstance(data, dict) else 'List data'}")

async def test_product_search_with_store(session, headers, store_id):
    """Test product search endpoints with store ID"""
    print("🔍 TESTING PRODUCT SEARCH WITH STORE ID")
    print("-" * 45)
    
    search_endpoints = [
        f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/stores/{store_id}/products/search?searchTerm=milk&limit=5',
        f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/products/search?storeId={store_id}&searchTerm=milk&limit=5',
        f'https://api.pcexpress.ca/pcx-bff/api/v1/stores/{store_id}/products/search?searchTerm=milk&limit=5'
    ]
    
    for endpoint in search_endpoints:
        print(f"🔍 Testing: {endpoint.split('/')[-1].split('?')[0]}")
        
        try:
            async with session.get(endpoint, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                status = response.status
                print(f"   Status: {status}")
                
                if status == 200:
                    data = await response.json()
                    print(f"   ✅ PRODUCT SEARCH WORKING! Results: {len(str(data))} chars")
                    
                    # Look for products in response
                    products = []
                    if isinstance(data, dict):
                        products = (data.get('products') or 
                                  data.get('results') or 
                                  data.get('items') or [])
                    
                    if products:
                        print(f"   🔍 Found {len(products)} products:")
                        for i, product in enumerate(products[:3]):
                            name = product.get('name', product.get('title', 'Unknown'))
                            price = product.get('price', 'No price')
                            print(f"     {i+1}. {name} - {price}")
                    
                    return endpoint
                
                elif status == 404:
                    print(f"   ❌ Not Found")
                else:
                    text = await response.text()
                    print(f"   ⚠️ {status}: {text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

async def test_cart_modification(session, headers, working_cart_endpoint):
    """Test if we can modify the cart using a working endpoint"""
    print("🔧 TESTING CART MODIFICATION CAPABILITIES")
    print("-" * 50)
    
    cart_url = working_cart_endpoint['url']
    
    # Try different modification endpoints based on the working cart URL
    base_url = cart_url.split('/carts')[0] + '/carts'
    
    modification_tests = [
        {
            'method': 'OPTIONS',
            'url': cart_url,
            'description': 'Check allowed methods'
        },
        {
            'method': 'POST', 
            'url': base_url + '/items',
            'description': 'Add item endpoint test',
            'data': {'test': True}  # Just to test the endpoint
        }
    ]
    
    for test in modification_tests:
        print(f"🔧 Testing: {test['description']}")
        
        try:
            if test['method'] == 'OPTIONS':
                async with session.options(test['url'], headers=headers) as response:
                    allowed_methods = response.headers.get('Allow', 'None')
                    print(f"   Allowed methods: {allowed_methods}")
                    
                    if 'POST' in allowed_methods or 'PUT' in allowed_methods:
                        print(f"   ✅ Cart modification likely possible!")
                        
            elif test['method'] == 'POST':
                async with session.post(test['url'], headers=headers, json=test['data']) as response:
                    print(f"   POST Status: {response.status}")
                    
                    if response.status in [200, 201, 400]:  # 400 is OK for test data
                        print(f"   ✅ POST endpoint accessible!")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()

async def main():
    success = await test_cart_with_specific_ids()
    
    if success:
        print("\n🎉 CART ENDPOINTS DISCOVERED!")
        print("✅ Found working cart access with specific IDs")
        print("🛒 Cart data successfully retrieved")
        print("🔧 Ready to implement full cart editing!")
    else:
        print("\n💡 CART DISCOVERY RESULTS:")
        print("❌ No cart endpoints found with current IDs")
        print("🔄 May need to create/initialize cart first")
        print("🛒 Fallback: Use working Chrome extension approach")

if __name__ == "__main__":
    asyncio.run(main())