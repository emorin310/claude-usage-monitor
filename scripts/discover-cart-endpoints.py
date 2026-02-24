#!/usr/bin/env python3
"""
Discover Working Cart Endpoints for Zehrs API
Since some endpoints return 404, let's systematically find the right ones
"""

import asyncio
import aiohttp
import json

async def discover_cart_endpoints():
    """Try different cart endpoint variations to find working ones"""
    
    # Load JWT tokens
    with open('/home/magi/clawd/grocery-data/jwt_tokens.json', 'r') as f:
        token_data = json.load(f)
    
    access_token = token_data['access_token']
    customer_id = token_data.get('user_id', '')
    
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
    
    print("🔍 DISCOVERING WORKING CART ENDPOINTS")
    print("=" * 45)
    print(f"🔑 Using JWT for customer: {customer_id}")
    print()
    
    # All possible endpoint variations to try
    endpoint_variations = [
        # Direct cart endpoints
        'https://api.pcexpress.ca/pcx-bff/api/v1/cart',
        'https://api.pcexpress.ca/pcx-bff/api/v1/carts',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/cart',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/carts',
        
        # Customer-based cart endpoints
        f'https://api.pcexpress.ca/pcx-bff/api/v1/customers/{customer_id}/cart',
        f'https://api.pcexpress.ca/pcx-bff/api/v1/customers/{customer_id}/carts',
        f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/customers/{customer_id}/cart',
        f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/customers/{customer_id}/carts',
        
        # Store-based cart endpoints  
        'https://api.pcexpress.ca/pcx-bff/api/v1/stores/0533/cart',
        'https://api.pcexpress.ca/pcx-bff/api/v1/stores/0533/carts',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/stores/0533/cart',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/stores/0533/carts',
        
        # V2 endpoints (from our earlier tests)
        'https://api.pcexpress.ca/pcx-bff/api/v2/ecommerce/zehrs/cart',
        'https://api.pcexpress.ca/pcx-bff/api/v2/ecommerce/zehrs/carts',
        f'https://api.pcexpress.ca/pcx-bff/api/v2/ecommerce/zehrs/customers/{customer_id}/cart',
        f'https://api.pcexpress.ca/pcx-bff/api/v2/ecommerce/zehrs/customers/{customer_id}/carts',
        
        # Product search endpoints
        'https://api.pcexpress.ca/pcx-bff/api/v1/products/search?searchTerm=milk&limit=5',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/products/search?searchTerm=milk&limit=5',
        'https://api.pcexpress.ca/pcx-bff/api/v1/stores/0533/products/search?searchTerm=milk&limit=5',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/stores/0533/products/search?searchTerm=milk&limit=5',
        
        # Order endpoints
        f'https://api.pcexpress.ca/pcx-bff/api/v1/customers/{customer_id}/orders',
        f'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/customers/{customer_id}/orders',
        'https://api.pcexpress.ca/pcx-bff/api/v1/orders',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/orders',
        
        # User/customer profile variations
        'https://api.pcexpress.ca/pcx-bff/api/v1/user/profile',
        'https://api.pcexpress.ca/pcx-bff/api/v1/user',
        'https://api.pcexpress.ca/pcx-bff/api/v1/customer',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/customer',
        
        # Other common endpoints
        'https://api.pcexpress.ca/pcx-bff/api/v1/deals',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/deals',
        'https://api.pcexpress.ca/pcx-bff/api/v1/promotions',
        'https://api.pcexpress.ca/pcx-bff/api/v1/favorites',
        'https://api.pcexpress.ca/pcx-bff/api/v1/user/favorites'
    ]
    
    async with aiohttp.ClientSession() as session:
        working_endpoints = []
        
        for i, endpoint in enumerate(endpoint_variations, 1):
            endpoint_name = endpoint.split('/')[-1].split('?')[0] or endpoint.split('/')[-2]
            print(f"🔍 [{i:2d}/{len(endpoint_variations)}] Testing: {endpoint_name}")
            print(f"   URL: {endpoint}")
            
            try:
                async with session.get(
                    endpoint, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    status = response.status
                    print(f"   Status: {status}")
                    
                    if status == 200:
                        try:
                            data = await response.json()
                            print(f"   ✅ SUCCESS! Data: {len(str(data))} chars")
                            
                            working_endpoints.append({
                                'endpoint': endpoint,
                                'name': endpoint_name,
                                'status': status,
                                'data_size': len(str(data)),
                                'sample_data': str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                            })
                            
                            # Save successful response
                            filename = f"/home/magi/clawd/grocery-data/working_{endpoint_name}_{i}.json"
                            with open(filename, 'w') as f:
                                json.dump(data, f, indent=2)
                            print(f"   💾 Saved: {filename}")
                            
                            # Special analysis for cart data
                            if 'cart' in endpoint_name.lower():
                                if isinstance(data, dict):
                                    items = data.get('items', data.get('cartItems', data.get('lineItems', [])))
                                    if items:
                                        print(f"   🛒 CART FOUND: {len(items)} items!")
                                    else:
                                        print(f"   📭 Cart structure found but empty")
                                elif isinstance(data, list):
                                    print(f"   🛒 CART LIST: {len(data)} items")
                            
                            # Analysis for product search
                            elif 'search' in endpoint_name.lower() or 'product' in endpoint_name.lower():
                                if isinstance(data, dict):
                                    products = data.get('products', data.get('results', data.get('items', [])))
                                    if products:
                                        print(f"   🔍 PRODUCTS FOUND: {len(products)} results!")
                                    
                        except json.JSONDecodeError:
                            text = await response.text()
                            print(f"   📝 Non-JSON response: {text[:100]}...")
                            
                            working_endpoints.append({
                                'endpoint': endpoint,
                                'name': endpoint_name,
                                'status': status,
                                'content_type': 'non-json',
                                'sample_text': text[:200]
                            })
                            
                    elif status == 401:
                        print(f"   ❌ Unauthorized")
                    elif status == 404:
                        print(f"   ❌ Not Found")
                    elif status == 403:
                        print(f"   ❌ Forbidden")
                    else:
                        try:
                            text = await response.text()
                            print(f"   ⚠️ Status {status}: {text[:100]}...")
                        except:
                            print(f"   ⚠️ Status {status}: (no response text)")
                            
            except asyncio.TimeoutError:
                print(f"   ⏰ Timeout")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print()
        
        # Summary of working endpoints
        print("🎯 ENDPOINT DISCOVERY RESULTS")
        print("=" * 35)
        
        if working_endpoints:
            print(f"🎉 SUCCESS! Found {len(working_endpoints)} working endpoints:")
            
            for endpoint in working_endpoints:
                print(f"\n✅ {endpoint['name']}")
                print(f"   URL: {endpoint['endpoint']}")
                print(f"   Status: {endpoint['status']}")
                if 'data_size' in endpoint:
                    print(f"   Data: {endpoint['data_size']} chars")
                    print(f"   Sample: {endpoint['sample_data']}")
            
            # Save working endpoints summary
            with open('/home/magi/clawd/grocery-data/working_endpoints_summary.json', 'w') as f:
                json.dump(working_endpoints, f, indent=2)
            
            print(f"\n💾 Working endpoints saved to: working_endpoints_summary.json")
            
            # Look for cart-specific endpoints
            cart_endpoints = [ep for ep in working_endpoints if 'cart' in ep['name'].lower()]
            if cart_endpoints:
                print(f"\n🛒 CART ENDPOINTS FOUND: {len(cart_endpoints)}")
                for ep in cart_endpoints:
                    print(f"   • {ep['name']}: {ep['endpoint']}")
            else:
                print(f"\n❌ No cart endpoints found - may need different approach")
                
        else:
            print(f"❌ No working endpoints found ({len(working_endpoints)}/{len(endpoint_variations)})")
            print("💡 This suggests:")
            print("   • JWT token may be expired")
            print("   • Different API base URL needed")  
            print("   • Additional authentication required")
            print("   • API endpoints have changed")
        
        return working_endpoints

async def main():
    working_endpoints = await discover_cart_endpoints()
    
    if working_endpoints:
        print("\n🚀 NEXT STEPS:")
        print("✅ Use working endpoints for cart operations")
        print("🔧 Build cart controller with discovered URLs")
        print("🛒 Test cart modification on working endpoints")
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. 🔄 Refresh JWT token (may be expired)")
        print("2. 🌐 Check network connectivity to API")
        print("3. 📋 Verify API base URL and version")
        print("4. 🍪 Try combining JWT + cookies approach")

if __name__ == "__main__":
    asyncio.run(main())