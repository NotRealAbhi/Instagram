from playwright.async_api import async_playwright
from Config import SESSION_ID

async def fetch_instagram_profile(username):
    try:
        print(f"[🌐 Visiting] https://www.instagram.com/{username}/")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            # Set session ID cookie for Instagram auth
            await context.add_cookies([{
                'name': 'sessionid',
                'value': SESSION_ID,
                'domain': '.instagram.com',
                'path': '/'
            }])

            page = await context.new_page()
            await page.goto(f'https://www.instagram.com/{username}/', wait_until="domcontentloaded")

            await page.wait_for_timeout(3000)

            # Profile picture
            profile_picture = await page.locator("img[data-testid='user-avatar']").first.get_attribute("src")

            # Name and bio from meta tags
            bio = await page.locator('meta[name="description"]').get_attribute("content")
            name = await page.locator('meta[property="og:title"]').get_attribute("content")

            # Basic reels/posts/highlights/stories from href scan
            links = await page.locator("a").all()
            reels = []
            posts = []
            highlights = []
            stories = []

            for link in links:
                href = await link.get_attribute("href")
                if href:
                    if "/reel/" in href:
                        reels.append("https://www.instagram.com" + href)
                    elif "/p/" in href:
                        posts.append("https://www.instagram.com" + href)
                    elif "/stories/highlights/" in href:
                        highlights.append("https://www.instagram.com" + href)
                    elif "/stories/" in href:
                        stories.append("https://www.instagram.com" + href)

            await browser.close()

            return {
                "profile_picture": profile_picture,
                "name": name or username,
                "bio": bio or "",
                "reels": list(set(reels)),
                "posts": list(set(posts)),
                "highlights": list(set(highlights)),
                "stories": list(set(stories))
            }

    except Exception as e:
        print(f"[❌ ERROR]: {e}")
        return None
        
