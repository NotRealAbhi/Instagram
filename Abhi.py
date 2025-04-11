from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Config import API_ID, API_HASH, BOT_TOKEN
from Handlers import Profile, Stories, Highlights, Posts, Reels, Zipper

app = Client("InstagramProfileBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await message.reply("👋 Send me an Instagram username (without @) to fetch profile info.")

@app.on_message(filters.text & filters.private)
async def username_handler(client, message):
    username = message.text.strip()
    await Profile.send_profile(client, message, username)

@app.on_callback_query(filters.regex(r"^(stories|highlights|posts|reels|zip):"))
async def callback_handler(client, query):
    cmd, username = query.data.split(":")
    if cmd == "stories":
        await Stories.send_stories(client, query.message, username)
    elif cmd == "highlights":
        await Highlights.send_highlights(client, query.message, username)
    elif cmd == "posts":
        await Posts.send_posts(client, query.message, username)
    elif cmd == "reels":
        await Reels.send_reels(client, query.message, username)
    elif cmd == "zip":
        await Zipper.send_zip(client, query.message, username)

app.run()
