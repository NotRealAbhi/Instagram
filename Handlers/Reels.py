import os
from Scraper import fetch_page, download_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup


async def fetch_reels(message, username):
    try:
        url = f"https://www.instagram.com/{username}/reels/"
        html = await fetch_page(url)

        if not html:
            return await message.reply("❌ Failed to load Reels page.")

        soup = BeautifulSoup(html, "html.parser")

        video_urls = []
        for video in soup.find_all("video"):
            src = video.get("src")
            if src:
                video_urls.append(src)

        if not video_urls:
            return await message.reply("❌ No Reels found.")

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data=f"profile_pic:{username}")]
        ])

        count = 0
        for i, url in enumerate(video_urls):
            file_name = f"{username}_reel_{i}.mp4"
            path = await download_file(url, file_name)
            if path:
                await message.reply_video(video=path, caption=f"🎞 Reel {i+1}", reply_markup=buttons)
                count += 1
                if count >= 5:  # Limit to 5 reels
                    break

    except Exception as e:
        await message.reply(f"❌ Error loading reels: {e}")
