from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Scraper import fetch_instagram_profile
from Config import BOT_TOKEN, SESSION_ID, API_ID, API_HASH
import re

bot = Client("InstaScraperBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

def extract_username(text: str):
    if "instagram.com" in text:
        match = re.search(r"instagram\.com/([^/?\s]+)", text)
        return match.group(1) if match else None
    elif text.startswith("@"):
        return text[1:]
    return text.strip()

@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "**Welcome!** 👋\nSend me any Instagram username or profile link to get details.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔒 Close", callback_data="close")]
        ])
    )

@bot.on_message(filters.text & ~filters.command(["start"]))
async def handle_username(_, message):
    username = extract_username(message.text)
    loading = await message.reply_text("🔍 Scraping profile... Please wait.")

    data = await fetch_instagram_profile(username)
    if not data:
        await loading.edit("❌ Failed to fetch profile data. Check username and session.")
        return

    buttons = [
        [InlineKeyboardButton("📸 Profile Pic", url=data["profile_picture"])],
        [
            InlineKeyboardButton("🎞️ Reels", callback_data=f"reels_{username}"),
            InlineKeyboardButton("🖼️ Posts", callback_data=f"posts_{username}")
        ],
        [
            InlineKeyboardButton("🧵 Highlights", callback_data=f"highlights_{username}"),
            InlineKeyboardButton("⏳ Stories", callback_data=f"stories_{username}")
        ],
        [
            InlineKeyboardButton("🗂️ ZIP All", callback_data=f"zip_{username}"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]

    await loading.edit_text(
        f"**👤 Name:** `{data.get('name', 'N/A')}`\n**📝 Bio:** {data.get('bio', 'No bio.')}```",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query()
async def callback_handler(_, query):
    data = query.data

    if data == "close":
        await query.message.delete()
        return

    try:
        action, username = data.split("_", 1)
    except Exception as e:
        await query.answer("Invalid callback data.")
        return

    await query.answer("⏳ Fetching, please wait...", show_alert=False)
    profile = await fetch_instagram_profile(username)

    if not profile:
        await query.message.reply_text("❌ Failed to refetch profile data.")
        return

    if action == "reels":
        reels = "\n".join(profile.get("reels", [])) or "No reels found."
        await query.message.reply_text(f"🎞️ **Reels:**\n{reels}")
    elif action == "posts":
        posts = "\n".join(profile.get("posts", [])) or "No posts found."
        await query.message.reply_text(f"🖼️ **Posts:**\n{posts}")
    elif action == "highlights":
        highlights = "\n".join(profile.get("highlights", [])) or "No highlights found."
        await query.message.reply_text(f"🧵 **Highlights:**\n{highlights}")
    elif action == "stories":
        stories = "\n".join(profile.get("stories", [])) or "No stories found."
        await query.message.reply_text(f"⏳ **Stories:**\n{stories}")
    elif action == "zip":
        await query.message.reply_text("🗂️ ZIP feature coming soon!")
    else:
        await query.answer("Unknown action!", show_alert=True)

bot.run()
