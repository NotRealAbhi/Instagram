import asyncio
import requests
from Config import SESSION_ID
from playwright.async_api import async_playwright

async def fetch_instagram_profile(username):
    try:
        # Launch Playwright browser
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # You can set headless=False for debugging
            context = await browser.new_context()  # Create a context without cookies

            # Now add the cookies
            cookies = [{
                'name': 'sessionid',
                'value': SESSION_ID,
                'domain': '.instagram.com'
                'path': '/'
            }]
            await context.add_cookies(cookies)  # Add cookies to the context'path': '/'

            # Create a new page in the context
            page = await context.new_page()

            # Go to the Instagram profile page
            await page.goto(f'https://www.instagram.com/{username}/', wait_until="domcontentloaded")

            # Wait for the page to load and the required selector
            await page.wait_for_selector('meta[name="description"]', timeout=30000)

            # Extract profile data (or any other data you need)
            profile_description = await page.locator('meta[name="description"]').get_attribute('content')

            if not profile_description:
                raise ValueError("Failed to extract profile description.")

            # Close browser after operation
            await browser.close()

            return profile_description  # Return valid content to the caller

    except Exception as e:
        print(f"❌ Error: {e}")
        return None  # Return None if something fails


username = 'soniya_rajput_9911'

async def main():
    profile_data = await fetch_instagram_profile(username)
    if profile_data:
        print(f"Profile Data: {profile_data}")
    else:
        print("Failed to fetch profile data.")

# Run the main function
asyncio.run(main())
