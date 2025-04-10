import json
import os
import aiofiles
import uuid
from bs4 import BeautifulSoup
from Scraper import fetch_page

async def fetch_profile_info(username):
    url = f"https://www.instagram.com/{username}/"
    html = await fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all("script", type="text/javascript")
    data_script = next((s for s in scripts if "window._sharedData" in s.text), None)

    if not data_script:
        return None, "❌ Couldn't extract profile data."

    json_text = data_script.string.split(" = ", 1)[1].rstrip(";")
    data = json.loads(json_text)
    user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

    name = user["full_name"]
    bio = user["biography"]
    profile_pic = user["profile_pic_url_hd"]

    filename = f"temp/{uuid.uuid4()}.jpg"
    async with aiofiles.open(filename, 'wb') as f:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(profile_pic)
            await f.write(resp.content)

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

    return filename, caption
