import os
import zipfile
import shutil
from pyrogram.types import Message
from Scraper import fetch_page, fetch_media_links, download_file


async def zip_all(message: Message, username: str):
    try:
        await message.reply("📦 Fetching all media and creating ZIP...")

        # Create temp folder
        temp_dir = f"temp/{username}"
        os.makedirs(temp_dir, exist_ok=True)

        # 1. Profile Pic & Info
        profile_pic, _ = await fetch_page(username)
        if profile_pic:
            shutil.copy(profile_pic, os.path.join(temp_dir, "profile_pic.jpg"))

        # 2. Posts, Reels, Stories, Highlights (use fake endpoints for simulation)
        media_types = {
            "posts": f"https://www.instagram.com/{username}/",
            "reels": f"https://www.instagram.com/{username}/reels/",
            "stories": f"https://www.instagram.com/stories/{username}/",
            "highlights": f"https://www.instagram.com/{username}/highlights/"
        }

        for media_name, url in media_types.items():
            html = await fetch_page(url)
            links = await fetch_media_links(html)
            for i, link in enumerate(links[:5]):
                file_path = await download_file(link, f"{media_name}_{i}.mp4")
                if file_path:
                    shutil.move(file_path, os.path.join(temp_dir, os.path.basename(file_path)))

        # Zip all media
        zip_path = f"{username}_all_media.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        # Send ZIP
        await message.reply_document(zip_path, caption=f"✅ All media for **{username}** zipped!")

    except Exception as e:
        await message.reply(f"❌ ZIP error: {e}")

    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(zip_path):
            os.remove(zip_path)
