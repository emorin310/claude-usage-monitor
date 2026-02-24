#!/usr/bin/env python3
"""
PC Express API Tester - Direct API Access to Zehrs Backend
Uses the discovered API endpoints to bypass web scraping entirely
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class PCExpressAPI:
    def __init__(self):
        self.base_url = "https://api.pcexpress.ca/pcx-bff/api/v1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Referer': 'https://www.zehrs.ca/',
            'site-banner': 'zehrs',
            'basesiteid': 'zehrs', 
            'x-channel': 'web',
            'is-iceberg-enabled': 'true',
            'is-helios-account': 'false'
        }
    
    async def test_pickup_locations(self):
        """Test the pickup locations endpoint we discovered"""
        url = f"{self.base_url}/pickup-locations?bannerIds=zehrs"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers) as response:
                    print(f"🏪 Pickup Locations API: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Success! Found {len(data.get('locations', []))} pickup locations")
                        
                        # Show first few locations
                        locations = data.get('locations', [])[:3]
                        for loc in locations:
                            print(f"  📍 {loc.get('name', 'Unknown')} - {loc.get('address', 'No address')}")
                        
                        return data
                    else:
                        text = await response.text()
                        print(f"❌ Error {response.status}: {text[:200]}")
                        return None
                        
            except Exception as e:
                print(f"❌ Request error: {e}")
                return None
    
    async def search_products_api(self, query="milk", limit=10):
        """Try to find product search API endpoint"""
        # Common API patterns to try
        search_endpoints = [
            f"/search?q={query}&banner=zehrs",
            f"/products/search?query={query}&limit={limit}",
            f"/search/products?term={query}",
            f"/search?searchTerm={query}&bannerIds=zehrs",
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in search_endpoints:
                url = f"{self.base_url}{endpoint}"
                print(f"🔍 Trying: {endpoint}")
                
                try:
                    async with session.get(url, headers=self.headers) as response:
                        print(f"   Status: {response.status}")
                        
                        if response.status == 200:
                            try:
                                data = await response.json()
                                print(f"   ✅ Success! Found data: {len(str(data))} chars")
                                
                                # Save the successful response
                                filename = f"/home/magi/clawd/grocery-data/api_search_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                with open(filename, 'w') as f:
                                    json.dump(data, f, indent=2)
                                print(f"   💾 Saved to: {filename}")
                                
                                return data
                                
                            except json.JSONDecodeError:
                                text = await response.text()
                                print(f"   📝 Non-JSON response: {text[:100]}...")
                        
                        elif response.status == 404:
                            print("   ❌ Endpoint not found")
                        else:
                            print(f"   ⚠️ Unexpected status: {response.status}")
                            
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                await asyncio.sleep(0.5)  # Be polite
        
        return None
    
    async def discover_more_endpoints(self):
        """Try to discover more API endpoints"""
        print("🔍 Discovering more API endpoints...")
        
        # Common e-commerce API patterns
        test_endpoints = [
            "/cart",
            "/cart/items", 
            "/user/profile",
            "/products/featured",
            "/products/categories",
            "/deals",
            "/promotions",
            "/stores",
            "/search/suggestions",
            "/user/orders",
            "/user/favorites",
            "/products/recommendations"
        ]
        
        async with aiohttp.ClientSession() as session:
            working_endpoints = []
            
            for endpoint in test_endpoints:
                url = f"{self.base_url}{endpoint}"
                
                try:
                    async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status in [200, 201, 400, 401]:  # These suggest the endpoint exists
                            working_endpoints.append({
                                'endpoint': endpoint,
                                'status': response.status,
                                'url': url
                            })
                            print(f"✅ {endpoint} - Status {response.status}")
                            
                            # Try to get a sample response
                            if response.status == 200:
                                try:
                                    data = await response.json()
                                    sample_keys = list(data.keys()) if isinstance(data, dict) else str(type(data))
                                    print(f"   📋 Response keys: {sample_keys}")
                                except:
                                    text = await response.text()
                                    print(f"   📝 Response preview: {text[:50]}...")
                        else:
                            print(f"❌ {endpoint} - Status {response.status}")
                            
                except asyncio.TimeoutError:
                    print(f"⏰ {endpoint} - Timeout")
                except Exception as e:
                    print(f"❌ {endpoint} - Error: {e}")
                
                await asyncio.sleep(0.3)  # Rate limiting
            
            # Save discovered endpoints
            if working_endpoints:
                filename = f"/home/magi/clawd/grocery-data/api_endpoints_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(working_endpoints, f, indent=2)
                print(f"💾 Working endpoints saved to: {filename}")
            
            return working_endpoints
    
    async def run_full_discovery(self):
        """Run complete API discovery and testing"""
        print("🚀 PC EXPRESS API DISCOVERY")
        print("=" * 40)
        
        # Test 1: Pickup locations (known working)
        print("\\n1. Testing Pickup Locations API...")
        locations = await self.test_pickup_locations()
        
        # Test 2: Product search attempts
        print("\\n2. Searching for Product Search API...")
        search_data = await self.search_products_api("milk")
        
        # Test 3: Endpoint discovery
        print("\\n3. Discovering More Endpoints...")
        endpoints = await self.discover_more_endpoints()
        
        # Summary
        print("\\n📊 DISCOVERY SUMMARY:")
        print("=" * 30)
        
        if locations:
            print(f"✅ Pickup Locations: {len(locations.get('locations', []))} stores found")
        
        if search_data:
            print("✅ Product Search: API endpoint found!")
        else:
            print("❌ Product Search: No working endpoint found")
        
        print(f"🔍 Total Working Endpoints: {len(endpoints) if endpoints else 0}")
        
        if endpoints:
            print("\\n🎯 Most Promising Endpoints:")
            for ep in endpoints[:5]:
                status_emoji = "✅" if ep['status'] == 200 else "⚠️"
                print(f"   {status_emoji} {ep['endpoint']} ({ep['status']})")
        
        return {
            'locations': locations,
            'search': search_data,
            'endpoints': endpoints
        }

# CLI interface
async def main():
    api = PCExpressAPI()
    
    print("🔑 PC Express API Tester")
    print("Using discovered Zehrs backend API")
    print()
    
    # Run full discovery
    results = await api.run_full_discovery()
    
    # Show next steps
    print("\\n🚀 NEXT STEPS:")
    if results['search']:
        print("1. ✅ Product search API found - can now get real product data!")
        print("2. 🛒 Try cart API endpoints for cart management") 
        print("3. 📦 Implement full grocery automation")
    else:
        print("1. 🔍 Continue endpoint discovery with different patterns")
        print("2. 📧 Try cart access with authentication headers")
        print("3. 🕷️ Combine API access with selective web scraping")

if __name__ == "__main__":
    asyncio.run(main())