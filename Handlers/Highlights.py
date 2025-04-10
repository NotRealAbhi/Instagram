import os
from Scraper import fetch_highlights_data

async def fetch_highlights(message, username):
    try:
        highlights = await fetch_highlights_data(username)
        if not highlights:
            return await message.reply("❌ No highlights found.")

        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        buttons = []
        for item in highlights[:10]:
            buttons.append([InlineKeyboardButton(text=item['title'], url=item['url'])])

        markup = InlineKeyboardMarkup(buttons)
        await message.reply("📂 Select a highlight to view:", reply_markup=markup)

    except Exception as e:
        await message.reply(f"❌ Failed to fetch highlights: `{e}`")
