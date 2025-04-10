# Abhi.py
import logging
from pyrogram import Client, InlineKeyboardButton, InlineKeyboardMarkup, filters
from Handlers.Profile import get_profile_data
from Handlers.Stories import get_stories
from Handlers.Highlights import get_highlights
from Handlers.Posts import get_posts
from Handlers.Reels import get_reels
from Handlers.Zipper import zip_media
from Config import API_ID, API_HASH, BOT_TOKEN
import os

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize the Pyrogram client (Telegram bot)
app = Client("InstagramBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    # Send a welcome message with inline keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Profile", callback_data="profile"),
            InlineKeyboardButton("Stories", callback_data="stories")
        ],
        [
            InlineKeyboardButton("Highlights", callback_data="highlights"),
            InlineKeyboardButton("Posts", callback_data="posts")
        ],
        [
            InlineKeyboardButton("Reels", callback_data="reels"),
            InlineKeyboardButton("Zip Media", callback_data="zip_media")
        ]
    ])
    await message.reply("Welcome to Instagram Scraper Bot! Please choose an option below.", reply_markup=keyboard)

@app.on_callback_query(filters.regex('^(profile|stories|highlights|posts|reels|zip_media)$'))
async def handle_buttons(client, callback_query):
    username = callback_query.message.text.split(":", 1)[1].strip() if ":" in callback_query.message.text else None
    
    if not username:
        await callback_query.message.reply(
            "Please send the Instagram username you want to scrape (e.g., soniya_rajput_9911).",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Cancel", callback_data="cancel")]
            ])
        )
        return

    media_files = []  # List to store media files

    if callback_query.data == "profile":
        profile_data = await get_profile_data(username)
        await callback_query.message.reply(profile_data)

    elif callback_query.data == "stories":
        stories_data = await get_stories(username)
        await callback_query.message.reply(stories_data)

    elif callback_query.data == "highlights":
        highlights_data = await get_highlights(username)
        await callback_query.message.reply(highlights_data)

    elif callback_query.data == "posts":
        posts_data = await get_posts(username)
        await callback_query.message.reply(posts_data)

    elif callback_query.data == "reels":
        reels_data = await get_reels(username)
        await callback_query.message.reply(reels_data)

    elif callback_query.data == "zip_media":
        # Collect media for zipping
        profile_data = await get_profile_data(username)
        media_files.append(profile_data)  # Example: profile picture file
        posts_data = await get_posts(username)
        media_files.extend(posts_data)  # Example: post images/videos
        # Add more media as needed (stories, highlights, reels)

        # Create zip of the collected media files
        zip_filename = zip_media(media_files)

        # Send the ZIP file
        await callback_query.message.reply_document(document=zip_filename)

        # Remove the zip file after sending
        os.remove(zip_filename)

@app.on_message(filters.text)
async def ask_for_username(client, message):
    if message.text:
        username = message.text.strip()
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Profile", callback_data=f"profile:{username}"),
                InlineKeyboardButton("Stories", callback_data=f"stories:{username}")
            ],
            [
                InlineKeyboardButton("Highlights", callback_data=f"highlights:{username}"),
                InlineKeyboardButton("Posts", callback_data=f"posts:{username}")
            ],
            [
                InlineKeyboardButton("Reels", callback_data=f"reels:{username}"),
                InlineKeyboardButton("Zip Media", callback_data=f"zip_media:{username}")
            ]
        ])
        await message.reply(f"Now choose the data you want to fetch for {username}:", reply_markup=keyboard)

@app.on_callback_query(filters.regex('^cancel$'))
async def cancel(client, callback_query):
    await callback_query.message.reply("You have cancelled the action. Type any text to restart the process.")
    await callback_query.message.delete()

if __name__ == "__main__":
    app.run()
