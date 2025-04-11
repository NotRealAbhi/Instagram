import os
import aiohttp
from pyrogram.types import InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton
from Scraper import get_browser
from Config import TEMP_DIR

async def send_reels(client, message, username):
    browser = await get_browser()
    page = await browser.new_page()

    try:
        await page.goto(f"https://www.instagram.com/{username}/reels/", timeout=60000)
        await page.wait_for_selector("video", timeout=15000)

        video_elements = await page.locator("video").all()
        video_urls = []

        for video in video_elements:
            url = await video.get_attribute("src")
            if url and url not in video_urls:
                video_urls.append(url)

        if not video_urls:
            await message.reply("⚠️ No reels found on this profile.")
            await browser.close()
            return

        # Limit to first 5 reels to avoid spam
        video_urls = video_urls[:5]

        folder_path = os.path.join(TEMP_DIR, f"{username}_reels")
        os.makedirs(folder_path, exist_ok=True)

        downloaded_files = []
        async with aiohttp.ClientSession() as session:
            for idx, url in enumerate(video_urls):
                filename = os.path.join(folder_path, f"reel_{idx + 1}.mp4")
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(filename, "wb") as f:
                            f.write(await resp.read())
                        downloaded_files.append(filename)

        if not downloaded_files:
            await message.reply("❌ Failed to download reels.")
        else:
            media = [InputMediaVideo(open(v, "rb")) for v in downloaded_files]
            await client.send_media_group(chat_id=message.chat.id, media=media)
            await message.reply("✅ Sent recent reels successfully!")

    except Exception as e:
        await message.reply(f"❌ Error while fetching reels for `{username}`.\n\nError: `{e}`")

    await browser.close()
