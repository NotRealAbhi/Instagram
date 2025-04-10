from playwright.async_api import async_playwright
from Config import SESSION_ID

async def fetch_instagram_profile(username):
    try:
        # Launch Playwright browser
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # Set headless=True for production, False for debugging
            context = await browser.new_context()  # Create context without cookies

            # Add cookies with the correct domain and path
            cookies = [{
                'name': 'sessionid',
                'value': SESSION_ID,
                'domain': '.instagram.com',  # domain for Instagram cookies
                'path': '/'  # path to make the cookie valid for the whole domain
            }]
            await context.add_cookies(cookies)  # Add cookies to the context

            # Create a new page in the context
            page = await context.new_page()

            # Go to the Instagram profile page
            await page.goto(f'https://www.instagram.com/{username}/', wait_until="domcontentloaded")

            # Wait for the page to load and try multiple selectors
            await page.wait_for_timeout(5000)  # Wait for 5 seconds to ensure the page has enough time to load

            # Try to get profile data using alternative methods if meta tag is not available
            profile_description = await page.locator('meta[name="description"]').get_attribute('content')
            if not profile_description:
                # Attempt to get the description from another meta tag or content
                profile_description = await page.locator('meta[property="og:description"]').get_attribute('content')

            if not profile_description:
                raise ValueError("Failed to extract profile description.")

            # Close browser after operation
            await browser.close()

            return profile_description  # Return valid content to the caller

    except Exception as e:
        print(f"❌ Error: {e}")
        return None  # Return None if something fails

# Example usage:
import asyncio

# Define session_id and username (example)
username = 'soniya_rajput_9911'

async def main():
    profile_data = await fetch_instagram_profile(username)
    if profile_data:
        print(f"Profile Data: {profile_data}")
    else:
        print("Failed to fetch profile data.")

# Run the main function
asyncio.run(main())
