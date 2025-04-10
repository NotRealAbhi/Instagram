from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from scraper import fetch_page
from Config import SESSION_ID
from playwright.async_api import async_playwright
import re
import asyncio


async def fetch_highlight_urls(username):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=SESSION_ID)
            page = await context.new_page()

            await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            await asyncio.sleep(3)

            highlights = await page.query_selector_all('._aam8')
            data = []
            for h in highlights:
                title = await h.inner_text()
                onclick = await h.get_attribute("onclick")
                href = await h.get_attribute("href")
                if href:
                    data.append({"title": title, "url": f"https://www.instagram.com{href}"})

            await browser.close()
            return data
    except Exception as e:
        print(f"❌ Error fetching highlights: {e}")
        return []


@Client.on_callback_query(filters.regex("highlights:(.*)"))
async def send_highlights(client, callback_query: CallbackQuery):
    username = callback_query.data.split(":")[1]
    msg = await callback_query.message.reply(f"⏳ Fetching highlights for @{username}...")

    highlights = await fetch_highlight_urls(username)

    if not highlights:
        return await msg.edit("❌ No highlights found.")

    for h in highlights[:5]:
        await callback_query.message.reply(f"🎯 **{h['title']}**\n🔗 {h['url']}")

    await msg.edit(f"✅ Found {len(highlights)} highlight albums for @{username}.")
  
