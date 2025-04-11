import os
import shutil
import zipfile
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Scraper import get_browser
from Config import TEMP_DIR

async def send_zip(client, message, username):
    base_path = os.path.join(TEMP_DIR, username)
    os.makedirs(base_path, exist_ok=True)

    try:
        browser = await get_browser()
        page = await browser.new_page()

        await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
        await page.wait_for_selector("img", timeout=10000)

        # Profile Picture
        try:
            pfp_url = await page.locator("header img").first.get_attribute("src")
            if pfp_url:
                await download_media(pfp_url, base_path, "profile.jpg")
        except:
            pass

        # Post Images
        try:
            await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            await page.wait_for_selector("article img", timeout=10000)
            imgs = await page.locator("article img").all()
            for i, img in enumerate(imgs[:5]):  # Limit to 5 posts
                src = await img.get_attribute("src")
                await download_media(src, base_path, f"post_{i+1}.jpg")
        except:
            pass

        # Reels (via preview thumbnails)
        try:
            await page.goto(f"https://www.instagram.com/{username}/reels/", timeout=60000)
            await page.wait_for_selector("video", timeout=10000)
            videos = await page.locator("video").all()
            for i, video in enumerate(videos[:5]):  # Limit to 5 reels
                src = await video.get_attribute("src")
                await download_media(src, base_path, f"reel_{i+1}.mp4")
        except:
            pass

        # Stories and Highlights coming soon...
        # Add similar download logic here when implemented.

        await browser.close()

        # Create ZIP
        zip_path = os.path.join(TEMP_DIR, f"{username}_data.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for root, _, files in os.walk(base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_path)
                    zipf.write(file_path, arcname)

        # Send ZIP
        if os.path.exists(zip_path):
            await client.send_document(
                chat_id=message.chat.id,
                document=zip_path,
                caption=f"📦 Download All Media for **{username}**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔁 Refresh", callback_data=f"zip:{username}")]
                ])
            )
        else:
            await message.reply("❌ ZIP creation failed.")

    except Exception as e:
        await message.reply(f"❌ Failed to create ZIP for `{username}`.\n\nError: `{e}`")

    # Cleanup
    shutil.rmtree(base_path, ignore_errors=True)
    if os.path.exists(zip_path):
        os.remove(zip_path)


async def download_media(url, folder, filename):
    import aiohttp
    path = os.path.join(folder, filename)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(path, "wb") as f:
                    f.write(await resp.read())
