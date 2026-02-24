#!/usr/bin/env python3
"""
Test the EXACT endpoint that worked before + hybrid JWT+Cookie approach
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone

async def test_exact_working_endpoint():
    """Test the exact customer profile endpoint that worked before"""
    
    # Load JWT tokens
    with open('/home/magi/clawd/grocery-data/jwt_tokens.json', 'r') as f:
        token_data = json.load(f)
    
    # Load cookies 
    with open('/home/magi/clawd/grocery-data/complete_cookies.json', 'r') as f:
        cookie_data = json.load(f)
    
    access_token = token_data['access_token']
    cookie_header = cookie_data['cookie_header']
    
    # Check token expiry
    exp_timestamp = token_data.get('expires_at', 0)
    exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    
    print("🔍 TESTING EXACT ENDPOINT THAT WORKED + TOKEN STATUS")
    print("=" * 60)
    print(f"🔑 JWT Token expires: {exp_time}")
    print(f"⏰ Current time: {now}")
    
    if now > exp_time:
        print("❌ JWT TOKEN EXPIRED!")
        token_expired = True
    else:
        time_left = exp_time - now
        print(f"✅ Token valid for: {time_left}")
        token_expired = False
    
    print()
    
    # Three different header approaches
    test_approaches = [
        {
            'name': 'JWT Only (Original Working)',
            'headers': {
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
        },
        {
            'name': 'Cookies Only (Fallback)',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en',
                'Content-Type': 'application/json',
                'Referer': 'https://www.zehrs.ca/',
                'Origin': 'https://www.zehrs.ca',
                'Cookie': cookie_header,
                'x-apikey': 'C1xujSegT5j3ap3yexJjqhOfELwGKYvz',
                'x-application-type': 'Web',
                'x-loblaw-tenant-id': 'ONLINE_GROCERIES',
                'business-user-agent': 'PCXWEB',
                'site-banner': 'zehrs'
            }
        },
        {
            'name': 'JWT + Cookies Hybrid (Best of Both)',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en',
                'Content-Type': 'application/json',
                'Referer': 'https://www.zehrs.ca/',
                'Origin': 'https://www.zehrs.ca',
                'Authorization': f'Bearer {access_token}',
                'Cookie': cookie_header,
                'x-apikey': 'C1xujSegT5j3ap3yexJjqhOfELwGKYvz',
                'x-application-type': 'Web',
                'x-loblaw-tenant-id': 'ONLINE_GROCERIES',
                'business-user-agent': 'PCXWEB',
                'site-banner': 'zehrs'
            }
        }
    ]
    
    # Test the EXACT endpoint that worked before
    test_endpoint = 'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers'
    
    async with aiohttp.ClientSession() as session:
        
        for approach in test_approaches:
            print(f"🔍 Testing: {approach['name']}")
            print(f"   Endpoint: {test_endpoint}")
            
            try:
                async with session.get(
                    test_endpoint,
                    headers=approach['headers'],
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    status = response.status
                    print(f"   Status: {status}")
                    
                    if status == 200:
                        try:
                            data = await response.json()
                            print(f"   ✅ SUCCESS! Customer profile accessible!")
                            print(f"   📊 Data size: {len(str(data))} chars")
                            
                            # Save the working approach
                            working_config = {
                                'approach': approach['name'],
                                'endpoint': test_endpoint,
                                'status': status,
                                'timestamp': datetime.now().isoformat(),
                                'data': data
                            }
                            
                            with open('/home/magi/clawd/grocery-data/working_customer_config.json', 'w') as f:
                                json.dump(working_config, f, indent=2)
                            
                            print(f"   💾 Working config saved!")
                            
                            # Now try cart endpoints with this working approach
                            await test_cart_with_working_auth(session, approach['headers'])
                            return True
                            
                        except json.JSONDecodeError:
                            text = await response.text()
                            print(f"   📝 Non-JSON response: {text[:100]}...")
                    
                    elif status == 401:
                        print(f"   ❌ Unauthorized - authentication failed")
                        if 'JWT' in approach['name']:
                            print(f"   💡 JWT token likely expired")
                    
                    elif status == 404:
                        print(f"   ❌ Not Found - endpoint may have changed")
                    
                    else:
                        text = await response.text()
                        print(f"   ⚠️ Status {status}: {text[:100]}...")
                        
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
            
            print()
        
        print("❌ No approaches worked for customer profile endpoint")
        return False

async def test_cart_with_working_auth(session, working_headers):
    """Test cart endpoints with the working authentication approach"""
    print("🛒 TESTING CART ENDPOINTS WITH WORKING AUTH")
    print("-" * 50)
    
    # Cart endpoint variations to try with working auth
    cart_endpoints = [
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers/carts',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/carts',
        'https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/stores/0533/carts',
        'https://api.pcexpress.ca/pcx-bff/api/v1/cart',
        'https://api.pcexpress.ca/pcx-bff/api/v1/carts'
    ]
    
    for endpoint in cart_endpoints:
        print(f"🔍 Testing cart: {endpoint.split('/')[-1]}")
        
        try:
            async with session.get(endpoint, headers=working_headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                status = response.status
                print(f"   Status: {status}")
                
                if status == 200:
                    try:
                        data = await response.json()
                        print(f"   ✅ CART ENDPOINT FOUND! Data: {len(str(data))} chars")
                        
                        # Save cart data
                        with open('/home/magi/clawd/grocery-data/working_cart_endpoint.json', 'w') as f:
                            json.dump({
                                'endpoint': endpoint,
                                'data': data,
                                'timestamp': datetime.now().isoformat()
                            }, f, indent=2)
                        
                        # Analyze cart contents
                        if isinstance(data, dict):
                            items = data.get('items', data.get('cartItems', []))
                            if items:
                                print(f"   🛒 Cart has {len(items)} items:")
                                for item in items[:3]:
                                    name = item.get('name', 'Unknown')
                                    qty = item.get('quantity', 1)
                                    print(f"     • {name} (qty: {qty})")
                            else:
                                print(f"   📭 Cart is empty")
                        
                        return endpoint
                        
                    except json.JSONDecodeError:
                        text = await response.text()
                        print(f"   📝 Non-JSON: {text[:100]}...")
                
                elif status == 404:
                    print(f"   ❌ Not Found")
                elif status == 401:
                    print(f"   ❌ Unauthorized")
                else:
                    text = await response.text()
                    print(f"   ⚠️ {status}: {text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("❌ No cart endpoints accessible with current auth")
    return None

async def main():
    success = await test_exact_working_endpoint()
    
    if success:
        print("\n🎉 AUTHENTICATION RECOVERED!")
        print("✅ Found working authentication approach")
        print("🛒 Cart endpoints tested with working auth")
    else:
        print("\n❌ ALL AUTHENTICATION APPROACHES FAILED")
        print("💡 Next steps:")
        print("1. 🔄 Refresh JWT token in browser")
        print("2. 🍪 Get fresh cookies")  
        print("3. 🌐 Check if Zehrs API structure changed")
        print("4. 📋 Use working Chrome extension approach instead")

if __name__ == "__main__":
    asyncio.run(main())