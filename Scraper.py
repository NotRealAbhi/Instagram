import os
import re
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from Config import SESSION_ID


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/120.0.0.0 Safari/537.36"
    )
}


import json
async def fetch_page(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Add session cookie for Instagram
        await context.add_cookies([{
            "name": "sessionid",
            "value": SESSION_ID,
            "domain": ".instagram.com",
            "path": "/"
        }])

        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")  # Wait for page to load
        
        try:
            await page.wait_for_selector("script[type='text/javascript']", timeout=60000)  # 1-minute timeout
        except Exception as e:
            print(f"Error: {e}")  # Log error if it occurs
            await browser.close()
            return None  # Return None if the page does not load properly or timeout occurs

        html = await page.content()  # Get full page content
        await browser.close()
        
        if not html:
            print("Error: No HTML content fetched")
            return None  # Return None if no HTML content is fetched

        return html


async def fetch_profile_info(username: str):
    url = f"https://www.instagram.com/{username}/"
    html = await fetch_page(url)

    if not html:
        raise Exception("Failed to fetch profile data.")  # This will give a clear error if fetch_page fails

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all("script", type="text/javascript")
    data_script = next((s for s in scripts if "window._sharedData" in s.text), None)

    if not data_script:
        raise Exception("Couldn't extract profile data.")

    try:
        json_text = data_script.string.split(" = ", 1)[1].rstrip(";")
        data = json.loads(json_text)
        user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        name = user["full_name"]
        bio = user["biography"]
        profile_pic = user["profile_pic_url_hd"]

        caption = (
            f"👤 **{name}**\n"
            f"🔗 **Username:** `{username}`\n"
            f"📖 **Bio:** {bio or 'N/A'}\n"
            f"📸 **Posts:** {user['edge_owner_to_timeline_media']['count']}\n"
            f"👥 **Followers:** {user['edge_followed_by']['count']}\n"
            f"👣 **Following:** {user['edge_follow']['count']}\n"
            f"🔒 **Private:** {user['is_private']}\n"
            f"✔ **Verified:** {user['is_verified']}"
        )

        return profile_pic, caption
    except Exception as e:
        raise Exception(f"Error fetching profile info: {e}")

async def fetch_stories(message, username):
    url = f"https://www.instagram.com/{username}/"
    html = await fetch_page(url)

    if not html:
        await message.reply("❌ Couldn't fetch stories.")
        return

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="text/javascript")
    data_script = next((s for s in scripts if "window._sharedData" in s.text), None)

    if not data_script:
        await message.reply("❌ Couldn't extract stories data.")
        return

    try:
        json_text = data_script.string.split(" = ", 1)[1].rstrip(";")
        data = json.loads(json_text)
        user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        stories = user.get('edge_owner_to_timeline_media', {}).get('edges', [])

        if not stories:
            await message.reply("❌ No stories available.")
            return

        story_urls = [story['node']['display_url'] for story in stories]
        await message.reply_text(f"Found {len(story_urls)} stories.")
        for url in story_urls:
            await message.reply_photo(url)
    except Exception as e:
        await message.reply(f"❌ Error fetching stories: {e}")


# Add additional functions for highlights, posts, reels, etc., following the same structure.




async def fetch_media_links(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="text/javascript")
    media_links = []

    for script in scripts:
        if script.string and "display_url" in script.string:
            urls = re.findall(r'"display_url":"([^"]+)"', script.string)
            media_links.extend([url.replace("\\u0026", "&") for url in urls])

    return media_links


async def download_file(url: str, filename: str) -> str:
    ext = os.path.splitext(url.split("?")[0])[-1]
    if not ext.startswith("."):
        ext = ".jpg"

    path = f"{filename}{ext}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download. Status code: {response.status}")
                content = await response.read()
                if not content:
                    raise Exception("Downloaded content is empty.")
                with open(path, "wb") as f:
                    f.write(content)
        return path

    except Exception as e:
        print(f"[ERROR] download_file() failed: {e}")
        return None
