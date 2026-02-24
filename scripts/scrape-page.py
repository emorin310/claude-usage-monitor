#!/usr/bin/env python3
"""
scrape-page.py - Headless Playwright scraper for JS-heavy pages
Usage: python3 scrape-page.py <url> [--screenshot] [--wait <selector>]
Outputs: cleaned markdown text to stdout
"""

import sys
import argparse
from playwright.sync_api import sync_playwright

def scrape(url, screenshot=False, wait_selector=None, timeout=15000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        
        try:
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=timeout)
            else:
                page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass  # Proceed with whatever loaded
        
        if screenshot:
            page.screenshot(path="/tmp/scrape-screenshot.png", full_page=True)
            print(f"[screenshot saved to /tmp/scrape-screenshot.png]", file=sys.stderr)
        
        # Extract readable text
        content = page.evaluate("""() => {
            // Remove noise elements
            ['script','style','nav','footer','iframe','noscript'].forEach(tag => {
                document.querySelectorAll(tag).forEach(el => el.remove());
            });
            return document.body ? document.body.innerText : '';
        }""")
        
        browser.close()
        return content.strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--screenshot", action="store_true")
    parser.add_argument("--wait", help="CSS selector to wait for")
    parser.add_argument("--timeout", type=int, default=15000)
    args = parser.parse_args()
    
    text = scrape(args.url, screenshot=args.screenshot,
                  wait_selector=args.wait, timeout=args.timeout)
    print(text[:50000])  # Cap output
