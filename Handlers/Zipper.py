import aiohttp
import os
import zipfile
import uuid
from Scraper import fetch_all_media_urls

async def zip_all(message, username):
    try:
        media_urls = await fetch_all_media_urls(username)
        if not media_urls:
            return await message.reply("❌ No media available to zip.")

        folder = f"temp/{uuid.uuid4()}"
        os.makedirs(folder, exist_ok=True)

        async with aiohttp.ClientSession() as session:
            for idx, media in enumerate(media_urls):
                url = media["url"]
                ext = ".mp4" if media["type"] == "video" else ".jpg"
                path = os.path.join(folder, f"media_{idx+1}{ext}")
                async with session.get(url) as resp:
                    with open(path, "wb") as f:
                        f.write(await resp.read())

        zip_path = f"{folder}.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for file in os.listdir(folder):
                zipf.write(os.path.join(folder, file), arcname=file)

        await message.reply_document(document=zip_path, caption=f"📦 All media from @{username}")

    except Exception as e:
        await message.reply(f"❌ ZIP creation failed: {e}")
      
