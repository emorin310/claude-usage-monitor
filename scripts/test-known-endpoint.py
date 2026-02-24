#!/usr/bin/env python3
"""
Test the exact API call that worked in the HAR file
"""

import asyncio
import aiohttp
import json

async def test_working_api():
    """Test the customer API that worked in HAR file"""
    
    # Exact headers from the working HAR request
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en",
        "business-user-agent": "PCXWEB",
        "connection": "keep-alive",
        "content-type": "application/json",
        "dnt": "1",
        "host": "api.pcexpress.ca",
        "origin": "https://www.zehrs.ca",
        "referer": "https://www.zehrs.ca/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-storage-access": "active",
        "site-banner": "zehrs",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "x-apikey": "C1xujSegT5j3ap3yexJjqhOfELwGKYvz",
        "x-application-type": "Web",
        "x-loblaw-tenant-id": "ONLINE_GROCERIES"
    }
    
    print("🧪 Testing exact API call that worked in HAR file...")
    
    async with aiohttp.ClientSession() as session:
        url = "https://api.pcexpress.ca/pcx-bff/api/v1/ecommerce/v2/zehrs/customers?syncRippleMembership=true"
        
        try:
            async with session.get(url, headers=headers) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ API call successful!")
                    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                    
                    # Save response
                    with open('/home/magi/clawd/grocery-data/customer_api_test.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    return True
                    
                elif response.status == 401:
                    print("❌ Unauthorized - missing authentication")
                    text = await response.text()
                    print(f"Response: {text[:200]}...")
                    
                else:
                    text = await response.text()
                    print(f"❌ Error {response.status}: {text[:200]}...")
                    
        except Exception as e:
            print(f"❌ Request error: {e}")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_working_api())