from playwright.async_api import async_playwright
from Config import SESSION_ID

async def fetch_instagram_profile(username):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            await context.add_cookies([{
                'name': 'sessionid',
                'value': SESSION_ID,
                'domain': '.instagram.com',
                'path': '/',
                'httpOnly': True,
                'secure': True,
            }])

            page = await context.new_page()
            await page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            name = await page.locator("header h1, header h2").first.inner_text()
            bio = await page.locator('meta[name="description"]').get_attribute('content')
            profile_pic_url = await page.locator("img[data-testid='user-avatar']").first.get_attribute("src")

            if not profile_pic_url:
                profile_pic_url = await page.locator("img[alt*='profile picture']").first.get_attribute("src")

            post_links = await page.eval_on_selector_all("article a", "els => els.map(e => e.href)")
            posts = [url for url in post_links if "/p/" in url]
            reels = [url for url in post_links if "/reel/" in url]

            highlights = await page.eval_on_selector_all("._aasp", "els => els.map(e => e.textContent.trim())")

            await page.goto(f"https://www.instagram.com/stories/{username}/", wait_until="load")
            await page.wait_for_timeout(2000)
            story_elements = await page.query_selector_all("video, img")
            stories = []
            for el in story_elements:
                src = await el.get_attribute("src")
                if src:
                    stories.append(src)

            await browser.close()

            return {
                "name": name or "Unknown",
                "bio": bio or "Not Found",
                "profile_picture": profile_pic_url,
                "posts": posts[:10],
                "reels": reels[:10],
                "highlights": highlights,
                "stories": stories
            }
    except Exception as e:
        print(f"[❌ SCRAPER ERROR]: {e}")
        return None
