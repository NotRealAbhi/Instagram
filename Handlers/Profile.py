import json
from bs4 import BeautifulSoup
from Scraper import fetch_page, download_file

async def fetch_profile_info(username):
    try:
        url = f"https://www.instagram.com/{username}/"
        html = await fetch_page(url)

        if not html:
            raise Exception("Empty response from Instagram")

        soup = BeautifulSoup(html, "html.parser")
        scripts = soup.find_all("script", type="text/javascript")
        data_script = next((s for s in scripts if "window._sharedData" in s.text), None)

        if not data_script:
            raise Exception("Profile data not found")

        json_text = data_script.string.split(" = ", 1)[1].rstrip(";")
        data = json.loads(json_text)

        user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        name = user.get("full_name", "N/A")
        bio = user.get("biography", "N/A")
        profile_pic_url = user.get("profile_pic_url_hd", user.get("profile_pic_url", ""))
        posts = user["edge_owner_to_timeline_media"]["count"]
        followers = user["edge_followed_by"]["count"]
        following = user["edge_follow"]["count"]
        is_private = user["is_private"]
        is_verified = user["is_verified"]

        caption = (
            f"👤 **{name}**\n"
            f"🔗 **Username:** `{username}`\n"
            f"📖 **Bio:** {bio or 'N/A'}\n"
            f"📸 **Posts:** {posts}\n"
            f"👥 **Followers:** {followers}\n"
            f"👣 **Following:** {following}\n"
            f"🔒 **Private:** {is_private}\n"
            f"✔ **Verified:** {is_verified}"
        )

        # Download the profile pic and return local path
        profile_pic_path = await download_file(profile_pic_url, f"{username}_profile.jpg")

        return profile_pic_path, caption

    except Exception as e:
        print(f"[handlers/profile.py] Error: {e}")
        raise Exception(f"❌ Error fetching profile info: {e}")
