import os
import aiohttp
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Scraper import get_browser
from Config import TEMP_DIR

async def send_stories(client, message, username):
    browser = await get_browser()
    page = await browser.new_page()

    try:
        await page.goto(f"https://www.instagram.com/stories/{username}/", timeout=60000)
        await page.wait_for_selector("video, img", timeout=10000)

        # Create temp folder
        folder_path = os.path.join(TEMP_DIR, f"{username}_stories")
        os.makedirs(folder_path, exist_ok=True)

        elements = await page.locator("video, img").all()
        story_urls = []

        for idx, el in enumerate(elements):
            src = await el.get_attribute("src")
            if src and src not in story_urls:
                story_urls.append(src)

        if not story_urls:
            await message.reply(f"😶 No public stories available for `{username}`.")
            await browser.close()
            return

        media_group = []
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(story_urls):
                filename = os.path.join(folder_path, f"story_{i}.jpg")
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(filename, "wb") as f:
                            f.write(await resp.read())

                        media_group.append(filename)

        # Send stories as album or single photos
        for story_path in media_group:
            await message.reply_photo(story_path)

        await message.reply("✅ All available stories have been sent.")

    except Exception as e:
        await message.reply(f"❌ Failed to fetch stories for `{username}`.\n\nError: `{e}`")

    await browser.close()
