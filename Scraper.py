from playwright.async_api import async_playwright
import asyncio
import json
import re
from Config import SESSION_ID

headers = {
    "cookie": f"sessionid={SESSION_ID};",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

async def fetch_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(extra_http_headers=headers)
        page = await context.new_page()
        await page.goto(url, timeout=60000)
        html = await page.content()
        await browser.close()
        return html

async def extract_shared_data(username):
    url = f"https://www.instagram.com/{username}/"
    html = await fetch_page(url)
    match = re.search(r"window\._sharedData = ({.*?});</script>", html)
    if match:
        shared_data = json.loads(match.group(1))
        return shared_data
    return None

async def fetch_page_data(username):
    data = await extract_shared_data(username)
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

async def fetch_profile_info(username):
    return await fetch_page_data(username)

async def fetch_stories_data(username):
    # Replace with actual scraping logic
    return [{"type": "photo", "url": "https://example.com/story1.jpg"}]

async def fetch_highlights_data(username):
    # Replace with actual scraping logic
    return [{"title": "Highlight 1", "url": "https://example.com/highlight1/"}]

async def fetch_post_data(username):
    # Replace with actual scraping logic
    return [{"type": "photo", "url": "https://example.com/post1.jpg"}]

async def fetch_reels_data(username):
    # Replace with actual scraping logic
    return [{"type": "video", "url": "https://example.com/reel1.mp4"}]

async def fetch_all_media_urls(username):
    posts = await fetch_post_data(username)
    reels = await fetch_reels_data(username)
    stories = await fetch_stories_data(username)
    return posts + reels + stories
