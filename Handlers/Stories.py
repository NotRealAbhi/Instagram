import os
import uuid
from Scraper import fetch_stories_data

async def fetch_stories(message, username):
    try:
        stories = await fetch_stories_data(username)
        if not stories:
            return await message.reply("❌ No active stories found.")

        media_group = []
        from pyrogram.types import InputMediaPhoto, InputMediaVideo

        for story in stories:
            media_type = story.get("type")
            url = story.get("url")
            caption = f"🧾 Story from @{username}"

            if media_type == "video":
                media_group.append(InputMediaVideo(media=url, caption=caption if len(media_group) == 0 else ""))
            else:
                media_group.append(InputMediaPhoto(media=url, caption=caption if len(media_group) == 0 else ""))

        await message.reply_media_group(media_group)

    except Exception as e:
        await message.reply(f"❌ Failed to fetch stories: `{e}`")
