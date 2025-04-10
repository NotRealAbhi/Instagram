import json
from Scraper import fetch_page
from bs4 import BeautifulSoup

async def fetch_profile_info(username: str):
    url = f"https://www.instagram.com/{username}/"
    html = await fetch_page(url)

    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="text/javascript")
    data_script = next((s for s in scripts if "window._sharedData" in s.text), None)

    if not data_script:
        raise Exception("Couldn't extract profile data.")

    json_text = data_script.string.split(" = ", 1)[1].rstrip(";")
    data = json.loads(json_text)
    
    try:
        user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        name = user.get("full_name", "N/A")
        bio = user.get("biography", "N/A")
        profile_pic = user.get("profile_pic_url_hd", "")

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
    except KeyError as e:
        raise Exception(f"Error extracting data: Missing key {e}")
