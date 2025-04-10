from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from Config import SESSION_ID
import json

async def fetch_instagram_data(username: str):
    """Fetch data from Instagram profile using Playwright and BeautifulSoup"""
    try:
        # Launch Playwright browser and set up the context with session cookies
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            # Add session cookies for authentication
            cookies = [{
                'name': 'sessionid',
                'value': SESSION_ID,  # session ID should be defined in Config.py
                'domain': '.instagram.com',
                'path': '/'
            }]
            await context.add_cookies(cookies)  # Add cookies to the context

            page = await context.new_page()
            await page.goto(f'https://www.instagram.com/{username}/', wait_until="domcontentloaded")

            # Wait for page to load
            await page.wait_for_timeout(5000)  # Wait for 5 seconds to ensure the page loads

            # Extract raw page content to parse with BeautifulSoup
            page_content = await page.content()
            soup = BeautifulSoup(page_content, "html.parser")

            # Find the script containing the JSON profile data
            scripts = soup.find_all("script", type="text/javascript")
            data_script = next((s for s in scripts if "window._sharedData" in s.text), None)

            if not data_script:
                raise Exception("Couldn't extract profile data.")

            # Extract and parse the JSON data from the script tag
            json_text = data_script.string.split(" = ", 1)[1].rstrip(";")
            data = json.loads(json_text)

            # Parse profile data
            user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
            name = user.get("full_name", "N/A")
            bio = user.get("biography", "N/A")
            profile_pic = user.get("profile_pic_url_hd", "")
            posts_count = user['edge_owner_to_timeline_media']['count']
            followers_count = user['edge_followed_by']['count']
            following_count = user['edge_follow']['count']
            is_private = user['is_private']
            is_verified = user['is_verified']

            # Prepare profile data for display
            caption = (
                f"👤 **{name}**\n"
                f"🔗 **Username:** `{username}`\n"
                f"📖 **Bio:** {bio or 'N/A'}\n"
                f"📸 **Posts:** {posts_count}\n"
                f"👥 **Followers:** {followers_count}\n"
                f"👣 **Following:** {following_count}\n"
                f"🔒 **Private:** {is_private}\n"
                f"✔ **Verified:** {is_verified}"
            )

            # Close the browser and return the profile data
            await browser.close()
            return profile_pic, caption

    except Exception as e:
        print(f"Error: {e}")  # Print any errors encountered during the scraping process
        return None, None  # Return None if scraping fails


# Example usage of the scraper
import asyncio

async def main():
    username = "43hi1_"
    profile_pic, caption = await fetch_instagram_data(username)
    
    if profile_pic and caption:
        print("Profile Pic URL:", profile_pic)
        print("Profile Description:", caption)
    else:
        print("Failed to fetch profile data.")

# Run the async main function
asyncio.run(main())
