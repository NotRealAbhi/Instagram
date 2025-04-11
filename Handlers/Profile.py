from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Scraper import get_browser

async def send_profile(client, message, username):
    browser = await get_browser()
    page = await browser.new_page()
    await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

    try:
        # Wait until at least the profile picture is visible
        await page.wait_for_selector("img", timeout=15000)

        # Try multiple selectors for name and bio with fallback
        try:
            name = await page.locator("header section h1").first.inner_text()
        except:
            name = "N/A"

        try:
            bio = await page.locator("section > div > h1 ~ div > span").first.inner_text()
        except:
            bio = "No bio available."

        try:
            pfp = await page.locator("header img").first.get_attribute("src")
        except:
            pfp = None

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🧿 Stories", callback_data=f"stories:{username}"),
             InlineKeyboardButton("🎯 Highlights", callback_data=f"highlights:{username}")],
            [InlineKeyboardButton("📸 Posts", callback_data=f"posts:{username}"),
             InlineKeyboardButton("🎥 Reels", callback_data=f"reels:{username}")],
            [InlineKeyboardButton("📦 Download All (ZIP)", callback_data=f"zip:{username}")]
        ])

        if pfp:
            await message.reply_photo(pfp, caption=f"👤 Name: {name}\n🧾 Bio: {bio}", reply_markup=buttons)
        else:
            await message.reply(f"👤 Name: {name}\n🧾 Bio: {bio}", reply_markup=buttons)

    except Exception as e:
        await message.reply(f"❌ Failed to fetch profile for `{username}`.\n\nError: `{e}`")

    await browser.close()
