import os
import shutil
from Scraper import get_browser

async def send_zip(client, message, username):
    folder = f"{username}_download"
    os.makedirs(folder, exist_ok=True)

    browser = await get_browser()
    page = await browser.new_page()
    await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

    imgs = await page.locator("article img").all()
    for idx, img in enumerate(imgs[:5]):
        url = await img.get_attribute("src")
        if url:
            await client.download_media(url, file_name=f"{folder}/{idx}.jpg")

    zip_path = shutil.make_archive(folder, 'zip', folder)
    await message.reply_document(zip_path, caption=f"📦 All-in-one ZIP for @{username}")

    shutil.rmtree(folder)
    os.remove(zip_path)
    await browser.close()
