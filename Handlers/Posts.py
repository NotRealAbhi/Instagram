import os
from Scraper import fetch_page, download_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup


async def fetch_posts(message, username):
    try:
        url = f"https://www.instagram.com/{username}/"
        html = await fetch_page(url)

        if not html:
            return await message.reply("❌ Failed to load profile page.")

        soup = BeautifulSoup(html, "html.parser")

        post_urls = []
        for video in soup.find_all("video"):
            src = video.get("src")
            if src:
                post_urls.append(src)

        for img in soup.find_all("img"):
            src = img.get("src")
            if src and "scontent" in src:
                post_urls.append(src)

        if not post_urls:
            return await message.reply("❌ No posts found.")

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data=f"profile_pic:{username}")]
        ])

        count = 0
        for i, url in enumerate(post_urls):
            ext = "mp4" if ".mp4" in url or "video" in url else "jpg"
            file_name = f"{username}_post_{i}.{ext}"
            path = await download_file(url, file_name)
            if path:
                await message.reply_document(document=path, caption=f"📸 Post {i+1}", reply_markup=buttons)
                count += 1
                if count >= 5:  # Limit to 5 posts for performance
                    break

    except Exception as e:
        await message.reply(f"❌ Error loading posts: {e}")
