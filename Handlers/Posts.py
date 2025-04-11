from Scraper import get_browser

async def send_posts(client, message, username):
    browser = await get_browser()
    page = await browser.new_page()
    await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

    imgs = await page.locator("article img").all()
    count = 0
    for img in imgs[:5]:
        url = await img.get_attribute("src")
        if url:
            await message.reply_photo(url)
            count += 1

    await message.reply(f"✅ Sent {count} latest posts.")
    await browser.close()
