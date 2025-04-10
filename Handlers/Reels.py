from Scraper import fetch_reels_data
from pyrogram.types import InputMediaVideo

async def fetch_reels(message, username):
    try:
        reels = await fetch_reels_data(username)
        if not reels:
            return await message.reply("❌ No reels found.")

        media_group = []

        for i, reel in enumerate(reels[:10]):
            media_group.append(InputMediaVideo(media=reel["url"], caption=f"🎞 Reel {i+1}" if i == 0 else ""))

        await message.reply_media_group(media_group)

    except Exception as e:
        await message.reply(f"❌ Error fetching reels: {e}")
      
