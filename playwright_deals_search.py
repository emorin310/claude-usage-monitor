
import asyncio
from playwright.async_api import Playwright, async_playwright, expect
from datetime import datetime, timedelta

async def search_hardware_deals(playwright: Playwright):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto("https://www.reddit.com/r/CanadianHardwareSwap/")

        # Try to find a more generic search icon/button
        # Often a button with text "Search" or a magnifying glass icon
        # Let's try a common Reddit search button class/data-testid if it exists
        # Otherwise, we might need to look for an SVG icon or title attribute
        
        # Option 1: Try clicking a button that explicitly says "Search" or has a search icon
        # This selector is a guess, may need to be adjusted based on Reddit's current UI
        search_button_selector = "#global-search-button, button[aria-label='Search'], div[data-redditstyle='globalSearch'] button"
        await page.locator(search_button_selector).first.click(timeout=10000)

        # Wait for the search input to become visible and type
        search_query = "16GB DDR4 ECC OR E5-2699 OR Xeon OR enterprise OR server OR homelab"
        await page.locator("input[placeholder='Search Reddit']").fill(search_query)
        await page.locator("input[placeholder='Search Reddit']").press("Enter")
        
        # Wait for search results to load
        await page.wait_for_selector("div[data-testid='post-container']", timeout=30000)

        # Extract results
        deals = []
        post_elements = await page.locator("div[data-testid='post-container']").all()

        for post_element in post_elements:
            title = await post_element.locator("h3").text_content()
            link = await post_element.locator("a[data-testid='post-title']").get_attribute("href")
            
            price = "N/A"
            if "price" in title.lower() or "$" in title:
                price = "Check post for price" 

            deals.append({"title": title, "link": f"https://www.reddit.com{link}", "price": price})

        return deals
    except Exception as e:
        print(f"An error occurred: {e}")
        await page.screenshot(path="/tmp/reddit_error.png")
        print("Screenshot saved to /tmp/reddit_error.png")
        return []
    finally:
        await browser.close()

async def main():
    async with async_playwright() as playwright:
        deals = await search_hardware_deals(playwright)
        
        print("Found the following hardware deals:")
        if deals:
            for deal in deals:
                print(f"Title: {deal['title']}")
                print(f"Link: {deal['link']}")
                print(f"Price: {deal['price']}")
                print("-" * 20)
        else:
            print("No deals found.")

if __name__ == "__main__":
    asyncio.run(main())
