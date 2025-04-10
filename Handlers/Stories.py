from pyrogram import Client, filters
from pyrogram.types import Message
from scraper import fetch_page
from Config import SESSION_ID
from playwright.async_api import async_playwright
import re
import aiofiles
import asyncio
import os
import uuid


async def fetch_stories(username):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=SESSION_ID)
            page = await context.new_page()
            await page.goto(f"https://www.instagram.com/stories/{username}/", timeout=60000)
            await asyncio.sleep(3)

            stories = []
            elements = await page.query_selector_all('video, img')
            for elem in elements:
                src = await elem.get_attribute('src')
                if src and "stories" in src:
                    stories.append(src)

            await browser.close()
            return stories
    except Exception as e:
        print(f"❌ Error fetching stories: {e}")
        return []


@Client.on_callback_query(filters.regex("stories:(.*)"))
async def send_stories(client, callback_query):
    username = callback_query.data.split(":")[1]
    msg = await callback_query.message.reply(f"⏳ Fetching stories from @{username}...")

    stories = await fetch_stories(username)

    if not stories:
        return await msg.edit("❌ No stories found or profile is private.")

    for story_url in stories:
        await callback_query.message.reply_media(story_url)

    await msg.edit(f"✅ Fetched {len(stories)} stories from @{username}.")
  
