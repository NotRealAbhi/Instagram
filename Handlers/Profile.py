import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from scraper import scrape_instagram

@Client.on_message(filters.text & filters.private)
async def fetch_profile_info(bot, message: Message):
    username = extract_username(message.text)
    if not username:
        return await message.reply_text("❌ Invalid Instagram username or link!")

    try:
        msg = await message.reply("🔍 Fetching profile info, please wait...")

        data = await scrape_instagram(username)

        caption = (
            f"👤 **{data['full_name']}**\n"
            f"🔗 **Username:** `{username}`\n"
            f"📖 **Bio:** {data['bio'] or 'N/A'}"
        )

        buttons = [
            [InlineKeyboardButton("📸 Profile Pic", callback_data=f"profile_pic:{username}"),
             InlineKeyboardButton("📖 Bio", callback_data=f"bio:{username}")],
            [InlineKeyboardButton("📸 Posts", callback_data=f"posts:{username}"),
             InlineKeyboardButton("🎞 Reels", callback_data=f"reels:{username}")],
            [InlineKeyboardButton("📂 Highlights", callback_data=f"highlights:{username}"),
             InlineKeyboardButton("📖 Stories", callback_data=f"stories:{username}")],
            [InlineKeyboardButton("⬇️ ZIP All", callback_data=f"zip:{username}")]
        ]

        await msg.delete()
        await message.reply_photo(
            photo=data['profile_pic'],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        await message.reply_text(f"❌ Failed to fetch profile: `{e}`")

def extract_username(text: str):
    import re
    match = re.search(r"(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)", text)
    return match.group(1) if match else text.strip().split()[0]
  
