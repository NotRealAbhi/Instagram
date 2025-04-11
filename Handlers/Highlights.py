import os
import aiohttp
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Scraper import get_browser
from Config import TEMP_DIR

async def send_highlights(client, message, username):
    browser = await get_browser()
    page = await browser.new_page()

    try:
        await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
        await page.wait_for_selector("div[role='button'] img", timeout=15000)

        highlights_elements = await page.locator("div[role='button'] img").all()
        if not highlights_elements:
            await message.reply("😕 No highlights found on this profile.")
            await browser.close()
            return

        folder_path = os.path.join(TEMP_DIR, f"{username}_highlights")
        os.makedirs(folder_path, exist_ok=True)

        highlight_urls = []
        for el in highlights_elements:
            url = await el.get_attribute("src")
            if url and url not in highlight_urls:
                highlight_urls.append(url)

        media_group = []
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(highlight_urls):
                filename = os.path.join(folder_path, f"highlight_{i}.jpg")
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(filename, "wb") as f:
                            f.write(await resp.read())
                        media_group.append(filename)

        if not media_group:
            await message.reply("🚫 Couldn't fetch highlight thumbnails.")
        else:
            for thumb in media_group:
                await message.reply_photo(photo=thumb)

            await message.reply("✅ Highlights thumbnails sent (Note: full playback not available yet).")

    except Exception as e:
        await message.reply(f"❌ Error while fetching highlights for `{username}`.\n\nError: `{e}`")

    await browser.close()
