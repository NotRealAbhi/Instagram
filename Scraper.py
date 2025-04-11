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
            url = f"https://www.instagram.com/{username.strip().lower()}/"
            print(f"[🌐 Visiting] {url}")
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)

            # Save debug HTML
            content = await page.content()
            with open("debug_profile.html", "w", encoding="utf-8") as f:
                f.write(content)

            # Get profile bio from meta tag
            bio = await page.locator('meta[name="description"]').get_attribute('content')

            # Get name from header or fallback from page
            name = await page.locator("header h1, header h2").first.inner_text()
            if not name:
                name = await page.locator("title").inner_text()

            # Profile picture fallback (new selector)
            profile_pic_url = await page.locator("img[alt*='profile']").first.get_attribute("src")
            if not profile_pic_url:
                profile_pic_url = await page.locator("img").first.get_attribute("src")

            await browser.close()

            if not name and not bio:
                raise Exception("❌ Instagram structure not loaded.")

            return {
                "name": name or "Unknown",
                "bio": bio or "Not Found",
                "profile_picture": profile_pic_url
            }

    except Exception as e:
        print(f"[❌ ERROR]: {e}")
        return None
