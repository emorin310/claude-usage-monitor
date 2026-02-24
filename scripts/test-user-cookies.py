#!/usr/bin/env python3
"""
Test User-Provided Cookies for Zehrs API Access
"""

import asyncio
import aiohttp
import json

async def test_user_cookies():
    """Test the cookies provided by user"""
    
    # Load user cookies
    with open('/home/magi/clawd/grocery-data/user_cookies.json', 'r') as f:
        cookie_data = json.load(f)
    
    cookie_header = cookie_data['cookie_header']
    
    # Headers with user's cookies
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Referer': 'https://www.zehrs.ca/',
        'Origin': 'https://www.zehrs.ca',
        'Cookie': cookie_header,
        'x-apikey': 'C1xujSegT5j3ap3yexJjqhOfELwGKYvz',
        'x-application-type': 'Web',
        'x-loblaw-tenant-id': 'ONLINE_GROCERIES',
        'business-user-agent': 'PCXWEB',
        'site-banner': 'zehrs',
        'is-helios-account': 'true'
    }
    
    print("🧪 TESTING USER'S COOKIES FOR API ACCESS")
    print("=" * 45)
    print(f"🍪 Cookie header length: {len(cookie_header)} chars")
    print(f"🔑 Key cookies: Origin_Session_Cookie, ttcsid_*")
    print()
    
    async with aiohttp.ClientSession() as session:
        
        # Test endpoints in order of likelihood to work
        test_endpoints = [
            {
                'name': 'Customer Info',
                'url': 'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers',
                'description': 'Basic customer data'
            },
            {
                'name': 'Customer Cart',
                'url': 'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/carts',
                'description': 'Shopping cart access'
            },
            {
                'name': 'Customer Orders',
                'url': 'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/orders',
                'description': 'Order history'
            }
        ]
        
        success_count = 0
        
        for endpoint in test_endpoints:
            print(f"🔍 Testing: {endpoint['name']}")
            print(f"   {endpoint['description']}")
            
            try:
                async with session.get(
                    endpoint['url'], 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            print(f"   ✅ SUCCESS! Data received: {len(str(data))} chars")
                            
                            # Save successful response
                            filename = f"/home/magi/clawd/grocery-data/api_success_{endpoint['name'].lower().replace(' ', '_')}.json"
                            with open(filename, 'w') as f:
                                json.dump(data, f, indent=2)
                            print(f"   💾 Data saved: {filename}")
                            
                            success_count += 1
                            
                            # Special handling for cart data
                            if 'cart' in endpoint['name'].lower():
                                items = []
                                if isinstance(data, dict):
                                    items = data.get('items', []) or data.get('cartItems', [])
                                elif isinstance(data, list):
                                    items = data
                                
                                if items:
                                    print(f"   🛒 CART ITEMS FOUND: {len(items)} items")
                                    for i, item in enumerate(items[:3]):
                                        name = item.get('name', item.get('productName', 'Unknown'))
                                        price = item.get('price', item.get('cost', 'No price'))
                                        print(f"     {i+1}. {name} - {price}")
                                else:
                                    print(f"   📭 Cart appears empty or data structure different")
                            
                        except json.JSONDecodeError:
                            text = await response.text()
                            print(f"   📝 Non-JSON response: {text[:100]}...")
                            
                    elif response.status == 401:
                        print(f"   ❌ Unauthorized - cookies may be insufficient or expired")
                        text = await response.text()
                        print(f"   📝 Error: {text[:100]}...")
                        
                    elif response.status == 404:
                        print(f"   ❌ Endpoint not found")
                        
                    else:
                        text = await response.text()
                        print(f"   ⚠️ Status {response.status}: {text[:100]}...")
                        
            except asyncio.TimeoutError:
                print(f"   ⏰ Timeout - endpoint may be slow")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print()
        
        # Summary
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 25)
        
        if success_count > 0:
            print(f"🎉 SUCCESS! {success_count}/{len(test_endpoints)} endpoints working")
            print("✅ Your cookies provide API access!")
            print("🛒 Can now potentially edit your cart programmatically")
            
            return True
        else:
            print(f"❌ No endpoints working ({success_count}/{len(test_endpoints)})")
            print("💡 This could mean:")
            print("   • Cookies are truncated/incomplete")
            print("   • Session has expired")
            print("   • Need additional authentication")
            print("   • Different API authentication method required")
            
            return False

async def main():
    success = await test_user_cookies()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("✅ API access confirmed with your session")
        print("🛒 Ready to implement cart editing functions")
        print("📊 Can now build full cart management system")
    else:
        print("\n🔧 ALTERNATIVES:")
        print("1. 🍪 Provide complete cookie values (not truncated)")
        print("2. 🧪 Run the local test script in your browser first")
        print("3. 🔄 Try refreshing your Zehrs session and re-extract cookies")

if __name__ == "__main__":
    asyncio.run(main())