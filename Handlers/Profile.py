from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Scraper import get_browser

async def send_profile(client, message, username):
    browser = await get_browser()
    page = await browser.new_page()
    await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

    name = await page.locator("header h1").inner_text()
    bio = await page.locator("div.-vDIg span").inner_text()
    pfp = await page.locator("img._aadp").get_attribute("src")

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧿 Stories", callback_data=f"stories:{username}"),
         InlineKeyboardButton("🎯 Highlights", callback_data=f"highlights:{username}")],
        [InlineKeyboardButton("📸 Posts", callback_data=f"posts:{username}"),
         InlineKeyboardButton("🎥 Reels", callback_data=f"reels:{username}")],
        [InlineKeyboardButton("📦 Download All (ZIP)", callback_data=f"zip:{username}")]
    ])

    await message.reply_photo(pfp, caption=f"👤 Name: {name}\n🧾 Bio: {bio}", reply_markup=buttons)
    await browser.close()
