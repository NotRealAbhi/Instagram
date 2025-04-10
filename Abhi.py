from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from Config import BOT_TOKEN, API_ID, API_HASH

from Handlers.Profile import fetch_profile_info
from Handlers.Stories import fetch_stories
from Handlers.Highlights import fetch_highlights
from Handlers.Posts import fetch_posts
from Handlers.Reels import fetch_reels
from Handlers.Zipper import zip_all

bot = Client("InstaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def get_username(text: str) -> str:
    import re
    match = re.search(r"(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)", text)
    if match:
        return match.group(1)
    return text.strip().split()[0]


@bot.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    await message.reply_text(
        "**👋 Welcome to Instagram Scraper Bot!**\n\n"
        "Send me any Instagram username or profile link to fetch profile pic, bio, stories, posts, reels, highlights, or download all!",
    )


@bot.on_message(filters.text & filters.private)
async def username_handler(_, message: Message):
    username = get_username(message.text)
    if not username:
        return await message.reply_text("❌ Invalid Instagram username!")

    try:
        profile_pic_path, caption = await fetch_profile_info(username)

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Profile Pic", callback_data=f"profile_pic:{username}"),
             InlineKeyboardButton("📖 Bio", callback_data=f"bio:{username}")],
            [InlineKeyboardButton("🎞 Reels", callback_data=f"reels:{username}"),
             InlineKeyboardButton("📸 Posts", callback_data=f"posts:{username}")],
            [InlineKeyboardButton("📂 Highlights", callback_data=f"highlights:{username}"),
             InlineKeyboardButton("📖 Stories", callback_data=f"stories:{username}")],
            [InlineKeyboardButton("⬇️ ZIP All", callback_data=f"zip:{username}")]
        ])

        await message.reply_photo(
            photo=profile_pic_path,
            caption=caption,
            reply_markup=buttons
        )

    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`")


@bot.on_callback_query()
async def handle_callbacks(_, query: CallbackQuery):
    try:
        data = query.data
        action, username = data.split(":", 1)

        if action == "profile_pic" or action == "bio":
            pic, caption = await fetch_profile_info(username)
            await query.message.reply_photo(pic, caption)

        elif action == "stories":
            await fetch_stories(query.message, username)

        elif action == "highlights":
            await fetch_highlights(query.message, username)

        elif action == "posts":
            await fetch_posts(query.message, username)

        elif action == "reels":
            await fetch_reels(query.message, username)

        elif action == "zip":
            await zip_all(query.message, username)

        await query.answer()

    except Exception as e:
        await query.message.reply_text(f"❌ Callback Error: {e}")
        await query.answer()

if __name__ == "__main__":
    print("🤖 Bot Started!")
    bot.run()
        
