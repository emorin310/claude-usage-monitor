#!/usr/bin/env python3
"""
Reddit Research Tool - No API key required
Searches Reddit communities for relevant technical discussions
"""

import asyncio
import json
import re
from playwright.async_api import async_playwright

class RedditResearcher:
    
    async def search_subreddit(self, query, subreddit="all", limit=10):
        """Search a specific subreddit"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            
            try:
                page = await browser.new_page()
                page.set_default_timeout(30000)
                
                # Reddit search URL
                search_url = f"https://www.reddit.com/r/{subreddit}/search/?q={query.replace(' ', '+')}&restrict_sr=1&sort=relevance"
                if subreddit == "all":
                    search_url = f"https://www.reddit.com/search/?q={query.replace(' ', '+')}&sort=relevance"
                
                print(f"🔍 Searching Reddit r/{subreddit} for: {query}")
                await page.goto(search_url, wait_until='networkidle')
                
                # Extract search results
                results = await page.evaluate(f'''
                    (() => {{
                        const posts = [];
                        
                        // Look for post containers
                        const postElements = document.querySelectorAll(
                            '[data-testid="post-container"], .Post, [data-click-id="body"], article'
                        );
                        
                        postElements.forEach((element, index) => {{
                            if (index >= {limit}) return;
                            
                            const text = element.textContent || '';
                            const links = Array.from(element.querySelectorAll('a')).map(a => a.href);
                            
                            // Find title
                            const titleElement = element.querySelector('h3, [data-testid="post-title"], .title a');
                            const title = titleElement ? titleElement.textContent.trim() : '';
                            
                            // Find subreddit
                            const subredditMatch = text.match(/r\\/([a-zA-Z0-9_]+)/);
                            const subreddit = subredditMatch ? subredditMatch[1] : '';
                            
                            // Find post URL
                            const postLink = links.find(link => link.includes('/comments/')) || '';
                            
                            if (title && title.length > 10) {{
                                posts.push({{
                                    title: title,
                                    subreddit: subreddit,
                                    link: postLink,
                                    preview: text.substring(0, 200),
                                    relevance_score: title.toLowerCase().includes('{query.lower()}') ? 10 : 5
                                }});
                            }}
                        }});
                        
                        return posts.sort((a, b) => b.relevance_score - a.relevance_score);
                    }})();
                ''')
                
                return results
                
            except Exception as e:
                print(f"❌ Reddit search error: {e}")
                return []
            finally:
                await browser.close()
    
    async def research_topic(self, topic, relevant_subreddits=None):
        """Research a topic across multiple relevant subreddits"""
        
        if not relevant_subreddits:
            relevant_subreddits = [
                "webscraping", "programming", "Python", "selenium",  
                "webdev", "devops", "automation", "MachineLearning"
            ]
        
        print(f"🔬 Researching '{topic}' across {len(relevant_subreddits)} subreddits...")
        
        all_results = {}
        
        for subreddit in relevant_subreddits[:3]:  # Limit to avoid rate limiting
            results = await self.search_subreddit(topic, subreddit, limit=5)
            if results:
                all_results[subreddit] = results
                print(f"✅ Found {len(results)} posts in r/{subreddit}")
            else:
                print(f"❌ No results in r/{subreddit}")
            
            await asyncio.sleep(2)  # Be polite to Reddit
        
        return all_results

# CLI interface
async def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python reddit-search.py <query> [subreddit]")
        print("Examples:")
        print("  python reddit-search.py 'grocery store automation'")
        print("  python reddit-search.py 'playwright login bypass' webscraping")
        return
    
    researcher = RedditResearcher()
    query = sys.argv[1]
    subreddit = sys.argv[2] if len(sys.argv) > 2 else "all"
    
    results = await researcher.search_subreddit(query, subreddit)
    
    if results:
        print(f"\\n🔍 Reddit Search Results for '{query}':")
        print("=" * 60)
        
        for i, post in enumerate(results, 1):
            print(f"{i}. {post['title']}")
            print(f"   📍 r/{post['subreddit']}")
            print(f"   🔗 {post['link']}")
            print(f"   📝 {post['preview'][:100]}...")
            print()
    else:
        print(f"❌ No results found for '{query}'")

if __name__ == "__main__":
    asyncio.run(main())