import os
import aiohttp
from pyrogram.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from Scraper import get_browser
from Config import TEMP_DIR

async def send_posts(client, message, username):
    browser = await get_browser()
    page = await browser.new_page()

    try:
        await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
        await page.wait_for_selector("article img", timeout=15000)

        image_elements = await page.locator("article img").all()
        image_urls = []

        for img in image_elements:
            url = await img.get_attribute("src")
            if url and url not in image_urls:
                image_urls.append(url)

        if not image_urls:
            await message.reply("⚠️ No posts found on this profile.")
            await browser.close()
            return

        # Limit to first 10 images to avoid spam
        image_urls = image_urls[:10]

        folder_path = os.path.join(TEMP_DIR, f"{username}_posts")
        os.makedirs(folder_path, exist_ok=True)

        downloaded_files = []
        async with aiohttp.ClientSession() as session:
            for idx, url in enumerate(image_urls):
                filename = os.path.join(folder_path, f"post_{idx + 1}.jpg")
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(filename, "wb") as f:
                            f.write(await resp.read())
                        downloaded_files.append(filename)

        if not downloaded_files:
            await message.reply("❌ Failed to download post images.")
        else:
            media = [InputMediaPhoto(open(p, "rb")) for p in downloaded_files]
            await client.send_media_group(chat_id=message.chat.id, media=media)
            await message.reply("✅ Sent recent posts successfully!")

    except Exception as e:
        await message.reply(f"❌ Error while fetching posts for `{username}`.\n\nError: `{e}`")

    await browser.close()
