# Scraper.py
from playwright.async_api import async_playwright
from Config import SESSION_ID

async def fetch_instagram_data(username):
    """ Fetch data from Instagram profile using Playwright """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            cookies = [{
                'name': 'sessionid',
                'value': SESSION_ID,
                'domain': '.instagram.com',
                'path': '/'
            }]
            await context.add_cookies(cookies)

            page = await context.new_page()
            await page.goto(f'https://www.instagram.com/{username}/', wait_until="domcontentloaded")

            await page.wait_for_timeout(5000)  # Wait for content to load

            # Scrape profile description
            profile_description = await page.locator('meta[name="description"]').get_attribute('content')
            if not profile_description:
                profile_description = await page.locator('meta[property="og:description"]').get_attribute('content')

            await browser.close()
            return profile_description

    except Exception as e:
        print(f"Error: {e}")
        return None
        
