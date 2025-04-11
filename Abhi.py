# main.py
import os
import zipfile
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from scraper import fetch_instagram_profile
from Config import BOT_TOKEN, API_ID, API_HASH

app = Client("InstagramProfileBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Handler to fetch profile information
@app.on_message(filters.command('start'))
async def start(client, message):
    await message.reply(
        "Welcome! Please send me the Instagram username to scrape.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Start Scraping", callback_data="start_scraping")]
        ])
    )

# Handler to process the username input
@app.on_message(filters.text)
async def fetch_profile(client, message):
    username = message.text
    profile_data = await fetch_instagram_profile(username)

    if profile_data:
        await message.reply(
            f"**Name**: {profile_data['name']}\n**Bio**: {profile_data['bio']}\n**Highlights**: {', '.join(profile_data['highlights'])}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Profile Picture", callback_data="profile_pic")],
                [InlineKeyboardButton("Posts", callback_data="posts")],
                [InlineKeyboardButton("Reels", callback_data="reels")],
                [InlineKeyboardButton("Highlights", callback_data="highlights")],
                [InlineKeyboardButton("Stories", callback_data="stories")],
                [InlineKeyboardButton("Download All Media", callback_data="download_all")],
                [InlineKeyboardButton("Close", callback_data="close")]
            ])
        )
    else:
        await message.reply("Failed to fetch profile data.")

# Handler for inline button to fetch profile picture
@app.on_callback_query(filters.regex('profile_pic'))
async def send_profile_picture(client, callback_query):
    username = callback_query.message.text.split(' ')[-1]  # Extract the username
    profile_data = await fetch_instagram_profile(username)
    if profile_data:
        await app.send_photo(callback_query.message.chat.id, profile_data['profile_picture'])

# Handler for inline button to fetch highlights
@app.on_callback_query(filters.regex('highlights'))
async def send_highlights(client, callback_query):
    username = callback_query.message.text.split(' ')[-1]
    profile_data = await fetch_instagram_profile(username)
    if profile_data:
        highlights_text = '\n'.join(profile_data['highlights'])
        await callback_query.message.reply(
            f"**Highlights:**\n{highlights_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Close", callback_data="close")]
            ])
        )

# Handler for inline button to fetch stories
@app.on_callback_query(filters.regex('stories'))
async def send_stories(client, callback_query):
    username = callback_query.message.text.split(' ')[-1]
    profile_data = await fetch_instagram_profile(username)
    if profile_data:
        # Assuming stories are fetched as URLs or media links
        stories_text = '\n'.join(profile_data['stories'])  # Customize based on your scraper logic
        await callback_query.message.reply(
            f"**Stories:**\n{stories_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Close", callback_data="close")]
            ])
        )

# Handler for inline button to fetch reels
@app.on_callback_query(filters.regex('reels'))
async def send_reels(client, callback_query):
    username = callback_query.message.text.split(' ')[-1]
    profile_data = await fetch_instagram_profile(username)
    if profile_data:
        # Assuming reels are fetched as URLs or media links
        reels_text = '\n'.join(profile_data['reels'])  # Customize based on your scraper logic
        await callback_query.message.reply(
            f"**Reels:**\n{reels_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Close", callback_data="close")]
            ])
        )

# Handler for inline button to fetch posts
@app.on_callback_query(filters.regex('posts'))
async def send_posts(client, callback_query):
    username = callback_query.message.text.split(' ')[-1]
    profile_data = await fetch_instagram_profile(username)
    if profile_data:
        # Assuming posts are fetched as URLs or media links
        posts_text = '\n'.join(profile_data['posts'])  # Customize based on your scraper logic
        await callback_query.message.reply(
            f"**Posts:**\n{posts_text}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Close", callback_data="close")]
            ])
        )

# Handler for inline button to download all media as ZIP
@app.on_callback_query(filters.regex('download_all'))
async def download_all_media(client, callback_query):
    username = callback_query.message.text.split(' ')[-1]
    profile_data = await fetch_instagram_profile(username)

    if profile_data:
        zip_filename = f"{username}_media.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            # Add posts and other media files
            for i, post in enumerate(profile_data['posts']):
                file_name = f"post_{i + 1}.jpg"
                zipf.write(post, file_name)

        with open(zip_filename, "rb") as file:
            await app.send_document(callback_query.message.chat.id, file)
            os.remove(zip_filename)  # Clean up the file after sending

# Handler for inline button to close the conversation
@app.on_callback_query(filters.regex('close'))
async def close_conversation(client, callback_query):
    await callback_query.message.delete()  # Delete the message to simulate a 'close' action

if __name__ == "__main__":
    app.run()
