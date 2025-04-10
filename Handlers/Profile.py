# handlers/profile.py

import json
import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from scraper import fetch_page
from bs4 import BeautifulSoup


def extract_username(text: str):
    match = re.search(r"(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)", text)
    return match.group(1) if match else text.strip().split()[0]


@Client.on_message(filters.text & filters.private)
async def profile_handler(client, message: Message):
    username = extract_username(message.text)
    if not username:
        return await message.reply("❌ Invalid Instagram username or link!")

    url = f"https://www.instagram.com/{username}/"
    html = await fetch_page(url)
    if not html:
        return await message.reply("❌ Couldn't load the profile page.")

    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="text/javascript")
    data_script = next((s for s in scripts if "window._sharedData" in s.text), None)

    if not data_script:
        return await message.reply("❌ Couldn't extract profile data.")

    try:
        json_text = data_script.string.split(" = ", 1)[1].rstrip(";")
        data = json.loads(json_text)
        user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        name = user.get("full_name", "N/A")
        bio = user.get("biography", "N/A")
        profile_pic = user.get("profile_pic_url_hd", "")
        posts_count = user["edge_owner_to_timeline_media"]["count"]
        followers = user["edge_followed_by"]["count"]
        following = user["edge_follow"]["count"]
        is_private = user["is_private"]
        is_verified = user["is_verified"]

        caption = (
            f"👤 **{name}**\n"
            f"🔗 **Username:** `{username}`\n"
            f"📖 **Bio:** {bio or 'N/A'}\n"
            f"📸 **Posts:** {posts_count}\n"
            f"👥 **Followers:** {followers}\n"
            f"👣 **Following:** {following}\n"
            f"🔒 **Private:** {is_private}\n"
            f"✔ **Verified:** {is_verified}"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Profile Pic", callback_data=f"profile_pic:{username}"),
             InlineKeyboardButton("📖 Bio", callback_data=f"bio:{username}")],
            [InlineKeyboardButton("📂 Highlights", callback_data=f"highlights:{username}"),
             InlineKeyboardButton("📖 Stories", callback_data=f"stories:{username}")],
            [InlineKeyboardButton("📸 Posts", callback_data=f"posts:{username}"),
             InlineKeyboardButton("🎞 Reels", callback_data=f"reels:{username}")],
            [InlineKeyboardButton("⬇️ ZIP All", callback_data=f"zip:{username}")]
        ])

        await message.reply_photo(photo=profile_pic, caption=caption, reply_markup=keyboard)

    except Exception as e:
        await message.reply(f"❌ Error parsing profile: {e}")
