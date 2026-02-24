#!/usr/bin/env python3
"""
Network Diagnostic Tool - Identify specific limitations
"""

import asyncio
import aiohttp
import time
from playwright.async_api import async_playwright

async def test_basic_http():
    """Test basic HTTP access"""
    print("🌐 Testing Basic HTTP Access...")
    
    async with aiohttp.ClientSession() as session:
        try:
            start_time = time.time()
            async with session.get('https://www.zehrs.ca/en', timeout=aiohttp.ClientTimeout(total=15)) as response:
                duration = time.time() - start_time
                print(f"✅ HTTP Request: {response.status} ({duration:.2f}s)")
                
                # Check response headers for bot detection
                headers = dict(response.headers)
                bot_indicators = ['akamai', 'cloudflare', 'bot', 'challenge']
                
                detected = []
                for key, value in headers.items():
                    if any(indicator in key.lower() or indicator in str(value).lower() 
                          for indicator in bot_indicators):
                        detected.append(f"{key}: {value}")
                
                if detected:
                    print("⚠️ Bot Detection Indicators Found:")
                    for indicator in detected[:3]:
                        print(f"   {indicator}")
                
                return True, response.status, duration
                
        except asyncio.TimeoutError:
            print("❌ HTTP Request: Timeout")
            return False, 0, 15
        except Exception as e:
            print(f"❌ HTTP Request: Error - {e}")
            return False, 0, 0

async def test_playwright_minimal():
    """Test minimal Playwright browser"""
    print("\n🎭 Testing Playwright Browser...")
    
    async with async_playwright() as p:
        try:
            start_time = time.time()
            
            # Try with minimal footprint
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            page = await browser.new_page()
            
            # Set realistic headers
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Test with shorter timeout
            page.set_default_timeout(10000)  # 10 seconds
            
            response = await page.goto('https://www.zehrs.ca/en', wait_until='domcontentloaded')
            duration = time.time() - start_time
            
            if response:
                print(f"✅ Playwright: {response.status} ({duration:.2f}s)")
                title = await page.title()
                print(f"   Page title: {title}")
                return True, response.status, duration
            else:
                print("❌ Playwright: No response")
                return False, 0, duration
                
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            print(f"❌ Playwright: Timeout after {duration:.2f}s")
            return False, 0, duration
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ Playwright: Error - {e} ({duration:.2f}s)")
            return False, 0, duration
            
        finally:
            try:
                await browser.close()
            except:
                pass

async def test_stealth_techniques():
    """Test various stealth techniques"""
    print("\n🕵️ Testing Stealth Techniques...")
    
    techniques = [
        {
            'name': 'User Agent Rotation',
            'args': [],
            'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        },
        {
            'name': 'Chrome DevTools Protocol',
            'args': ['--remote-debugging-port=0'],
            'headers': {}
        },
        {
            'name': 'Disable Automation Features',
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--exclude-switches=enable-automation',
                '--disable-extensions'
            ],
            'headers': {}
        }
    ]
    
    for technique in techniques:
        print(f"\n  Testing: {technique['name']}")
        
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage'] + technique['args']
                )
                
                page = await browser.new_page()
                
                if technique['headers']:
                    await page.set_extra_http_headers(technique['headers'])
                
                page.set_default_timeout(8000)  # 8 seconds
                
                start_time = time.time()
                response = await page.goto('https://www.zehrs.ca/en', wait_until='domcontentloaded')
                duration = time.time() - start_time
                
                if response and response.status == 200:
                    print(f"    ✅ Success! ({duration:.2f}s)")
                    title = await page.title()
                    if 'zehrs' in title.lower():
                        print(f"    🎯 Valid page loaded: {title}")
                        return technique['name']
                    else:
                        print(f"    ⚠️ Unexpected page: {title}")
                else:
                    print(f"    ❌ Failed: {response.status if response else 'No response'}")
                
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:50]}...")
            finally:
                try:
                    await browser.close()
                except:
                    pass
    
    return None

async def diagnose_network_limitation():
    """Complete network diagnostic"""
    print("🔍 ZEHRS NETWORK DIAGNOSTIC")
    print("=" * 40)
    
    # Test 1: Basic HTTP
    http_success, http_status, http_time = await test_basic_http()
    
    # Test 2: Playwright
    playwright_success, pw_status, pw_time = await test_playwright_minimal()
    
    # Test 3: Stealth techniques
    working_technique = await test_stealth_techniques()
    
    # Analysis
    print("\n📊 DIAGNOSTIC RESULTS")
    print("=" * 30)
    
    if http_success and not playwright_success:
        print("🎯 DIAGNOSIS: Anti-Bot Protection")
        print("   ✅ Basic HTTP works fine")
        print("   ❌ Browser automation blocked")
        print("   🔍 Likely: Akamai Bot Manager or similar")
        
        if working_technique:
            print(f"   ✅ SOLUTION FOUND: {working_technique}")
            return f"bot_protection_bypass:{working_technique}"
        else:
            print("   💡 Possible solutions:")
            print("     • Residential proxy")
            print("     • Advanced stealth techniques")
            print("     • Session stealing from real browser")
            return "bot_protection_advanced"
    
    elif not http_success:
        print("🌐 DIAGNOSIS: Network Connectivity Issue")
        print("   ❌ Basic HTTP fails")
        print("   💡 Possible causes:")
        print("     • Firewall blocking")
        print("     • Geographic restrictions")
        print("     • DNS issues")
        return "network_blocked"
    
    elif http_success and playwright_success:
        print("✅ DIAGNOSIS: Network Working Fine")
        print("   ✅ Both HTTP and Playwright work")
        print("   💡 Previous timeouts may have been temporary")
        return "network_ok"
    
    else:
        print("❓ DIAGNOSIS: Unclear")
        print("   Mixed results - needs deeper investigation")
        return "inconclusive"

async def main():
    diagnosis = await diagnose_network_limitation()
    
    print(f"\n🎯 FINAL DIAGNOSIS: {diagnosis}")
    
    if diagnosis.startswith("bot_protection"):
        print("\n🛠️ RECOMMENDED SOLUTIONS:")
        print("1. 🎭 Use advanced stealth techniques")
        print("2. 🔄 Session stealing from real browser")
        print("3. 📧 Focus on email receipt parsing")
        print("4. 🌐 Use residential proxy service")
    
    elif diagnosis == "network_ok":
        print("\n🚀 RECOMMENDED ACTION:")
        print("1. ✅ Retry the authentication harvest")
        print("2. 🎯 Network limitations were temporary")
        print("3. 🛒 Full system should work now")
    
    print(f"\n📋 SUMMARY FOR USER:")
    print(f"   Network Status: {diagnosis.replace('_', ' ').title()}")
    print(f"   Recommended Approach: {'API Access Possible' if diagnosis == 'network_ok' else 'Alternative Methods'}")

if __name__ == "__main__":
    asyncio.run(main())