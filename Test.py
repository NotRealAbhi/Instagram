import requests
from Config import SESSION_ID
import asyncio
from playwright.async_api import async_playwright

async def fetch_instagram_profile(username, session_id):
    # Launch the Playwright browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            cookies=[{
                'name': 'sessionid',
                'value': session_id,
                'domain': '.instagram.com'
            }]
        )
        page = await context.new_page()
        
        # Go to the Instagram profile URL
        await page.goto(f'https://www.instagram.com/{username}/')

        # Wait for the page to load
        await page.wait_for_selector('meta[name="description"]', timeout=30000)

        # Extract profile info (this could be more complex depending on what you want to scrape)
        profile_description = await page.locator('meta[name="description"]').get_attribute('content')

        # Close the browser
        await browser.close()
        
        return profile_description

# Example usage:
username = 'soniya_rajput_9911'  # Instagram username
session_id = 'SESSION_ID'  # Replace with your session ID

async def main():
    profile_data = await fetch_instagram_profile(username, session_id)
    print("Profile Data:", profile_data)

# Run the script
asyncio.run(main())
