import os
from playwright.async_api import async_playwright
from Config import SESSION_ID

async def fetch_instagram_profile(username):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            # Add Instagram session cookie
            await context.add_cookies([{
                "name": "sessionid",
                "value": SESSION_ID,
                "domain": ".instagram.com",
                "path": "/"
            }])

            page = await context.new_page()

            # Go to the profile page
            await page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Get name and bio from meta tag
            desc = await page.locator('meta[name="description"]').get_attribute('content')
            name = await page.locator("header h2, header h1").first.inner_text()
            profile_pic_url = await page.locator("img[data-testid='user-avatar']").first.get_attribute("src")

            # Fallback if image not found
            if not profile_pic_url:
                profile_pic_url = await page.locator("img[alt*='profile picture']").first.get_attribute("src")

            # Scroll to load posts and reels
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)

            post_links = await page.eval_on_selector_all("article a", "els => els.map(e => e.href)")
            posts = [url for url in post_links if "/p/" in url]
            reels = [url for url in post_links if "/reel/" in url]

            # Highlights
            highlights = await page.eval_on_selector_all("._aasp", "els => els.map(e => e.textContent.trim())")

            # Navigate to Stories page (if public stories exist)
            await page.goto(f"https://www.instagram.com/stories/{username}/", wait_until="load")
            await page.wait_for_timeout(2000)

            # Grab story URLs if available
            story_elements = await page.query_selector_all("video, img")
            stories = []
            for el in story_elements:
                src = await el.get_attribute("src")
                if src:
                    stories.append(src)

            await browser.close()

            return {
                "name": name or "Not Found",
                "bio": desc or "Not Found",
                "profile_picture": profile_pic_url,
                "posts": posts[:10],  # Limit to 10 for safety
                "reels": reels[:10],
                "highlights": highlights or [],
                "stories": stories or []
            }

    except Exception as e:
        print(f"❌ Scraper Error: {e}")
        return None
