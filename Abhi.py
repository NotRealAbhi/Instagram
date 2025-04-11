from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

from Handlers.Profile import send_profile
from Handlers.Stories import send_stories
from Handlers.Highlights import send_highlights
from Handlers.Posts import send_posts
from Handlers.Reels import send_reels
from Handlers.Zipper import send_zip

from Config import API_ID, API_HASH, BOT_TOKEN

bot = Client("InstaScraperBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@bot.on_message(filters.command("start"))
async def start_command(_, message: Message):
    await message.reply(
        "👋 Welcome to Instagram Scraper Bot!\n\n"
        "Send me any **Instagram username** to fetch profile details, posts, stories, reels, and more!",
    )


@bot.on_message(filters.text & ~filters.private & filters.group)
async def ignore_group(_, message: Message):
    await message.reply("❌ This bot only works in **private chat**.\nPlease send me a username here.")


@bot.on_message(filters.private & filters.text)
async def fetch_profile(_, message: Message):
    username = message.text.strip().replace("@", "")
    if not username:
        return await message.reply("❌ Please provide a valid username.")

    await send_profile(_, message, username)


@bot.on_callback_query()
async def callback_handler(_, query: CallbackQuery):
    if ":" not in query.data:
        return await query.answer("Invalid request!", show_alert=True)

    command, username = query.data.split(":", 1)

    if command == "stories":
        await send_stories(_, query.message, username)
    elif command == "highlights":
        await send_highlights(_, query.message, username)
    elif command == "posts":
        await send_posts(_, query.message, username)
    elif command == "reels":
        await send_reels(_, query.message, username)
    elif command == "zip":
        await send_zip(_, query.message, username)
    else:
        await query.answer("Unknown action.", show_alert=True)


if __name__ == "__main__":
    bot.run()
