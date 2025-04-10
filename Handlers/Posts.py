from Scraper import fetch_post_data
from pyrogram.types import InputMediaPhoto, InputMediaVideo

async def fetch_posts(message, username):
    try:
        posts = await fetch_post_data(username)
        if not posts:
            return await message.reply("❌ No posts found.")

        media_group = []

        for i, post in enumerate(posts[:10]):
            if post["type"] == "video":
                media_group.append(InputMediaVideo(media=post["url"], caption=f"📸 Post {i+1}" if i == 0 else ""))
            else:
                media_group.append(InputMediaPhoto(media=post["url"], caption=f"📸 Post {i+1}" if i == 0 else ""))

        await message.reply_media_group(media_group)

    except Exception as e:
        await message.reply(f"❌ Error fetching posts: {e}")
      
