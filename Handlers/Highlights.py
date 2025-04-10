import os
from Scraper import fetch_page, download_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup


async def fetch_highlights(message, username):
    try:
        url = f"https://www.instagram.com/stories/highlights/{username}/"
        html = await fetch_page(url)

        if not html:
            return await message.reply("❌ Failed to load highlights page.")

        soup = BeautifulSoup(html, "html.parser")

        highlight_urls = []
        for video in soup.find_all("video"):
            src = video.get("src")
            if src:
                highlight_urls.append(src)

        for img in soup.find_all("img"):
            src = img.get("src")
            if src and "stories" in src:
                highlight_urls.append(src)

        if not highlight_urls:
            return await message.reply("❌ No highlight stories found.")

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data=f"profile_pic:{username}")]
        ])

        for i, url in enumerate(highlight_urls):
            file_name = f"{username}_highlight_{i}.jpg" if ".jpg" in url else f"{username}_highlight_{i}.mp4"
            path = await download_file(url, file_name)
            if path:
                await message.reply_document(document=path, caption=f"📂 Highlight {i+1}", reply_markup=buttons)

    except Exception as e:
        await message.reply(f"❌ Error loading highlights: {e}")
