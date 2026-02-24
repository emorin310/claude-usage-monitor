#!/usr/bin/env python3
"""
Quick Cart Check - Direct API attempt
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def check_cart_direct():
    """Try direct cart API access"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Referer': 'https://www.zehrs.ca/',
        'site-banner': 'zehrs',
        'basesiteid': 'zehrs',
        'x-channel': 'web',
        'is-iceberg-enabled': 'true'
    }
    
    async with aiohttp.ClientSession() as session:
        cart_url = "https://api.pcexpress.ca/pcx-bff/api/v1/cart"
        
        try:
            async with session.get(cart_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"🛒 Cart API Status: {response.status}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        return data
                    except:
                        text = await response.text()
                        return {"error": "non_json", "content": text[:200]}
                
                elif response.status == 401:
                    return {"error": "unauthorized", "message": "Authentication required"}
                
                else:
                    text = await response.text()
                    return {"error": f"status_{response.status}", "content": text[:200]}
                    
        except Exception as e:
            return {"error": "request_failed", "message": str(e)}

async def main():
    print("🛒 QUICK CART CHECK")
    print("=" * 25)
    
    result = await check_cart_direct()
    
    if isinstance(result, dict) and "error" in result:
        if result["error"] == "unauthorized":
            print("🔐 Cart requires authentication")
            print("❌ Current status: Not logged in")
            print()
            print("💡 This means:")
            print("   • Authentication harvest didn't complete successfully")
            print("   • Need to complete login process")
            print("   • Cart access requires valid session tokens")
        else:
            print(f"❌ API Error: {result['error']}")
            if "content" in result:
                print(f"📝 Response: {result['content']}")
    
    else:
        print("✅ Cart access successful!")
        print("📊 Cart contents:")
        
        if isinstance(result, dict):
            items = result.get('items', [])
            total = result.get('total', 'Unknown')
            
            if items:
                for i, item in enumerate(items, 1):
                    name = item.get('name', item.get('description', 'Unknown item'))
                    price = item.get('price', item.get('cost', 'No price'))
                    qty = item.get('quantity', 1)
                    
                    print(f"  {i}. {name}")
                    print(f"     Quantity: {qty}")
                    print(f"     Price: {price}")
                    print()
                
                print(f"💰 Total: {total}")
            else:
                print("📭 Your cart is empty")
        else:
            print(f"📄 Raw response: {result}")

if __name__ == "__main__":
    asyncio.run(main())