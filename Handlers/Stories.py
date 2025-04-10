import os
from Scraper import fetch_page, download_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bs4 import BeautifulSoup

async def fetch_stories(message, username):
    try:
        url = f"https://www.instagram.com/stories/{username}/"
        html = await fetch_page(url)

        if not html:
            return await message.reply("❌ Failed to load stories page.")

        soup = BeautifulSoup(html, "html.parser")

        story_urls = []
        for video in soup.find_all("video"):
            src = video.get("src")
            if src:
                story_urls.append(src)

        for img in soup.find_all("img"):
            src = img.get("src")
            if src and "stories" in src:
                story_urls.append(src)

        if not story_urls:
            return await message.reply("❌ No stories found for this user.")

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data=f"profile_pic:{username}")]
        ])

        media_group = []
        for i, url in enumerate(story_urls):
            file_name = f"{username}_story_{i}.jpg" if ".jpg" in url else f"{username}_story_{i}.mp4"
            path = await download_file(url, file_name)
            if path:
                await message.reply_document(document=path, caption=f"📖 Story {i+1}", reply_markup=buttons)

    except Exception as e:
        await message.reply(f"❌ Error loading stories: {e}")
