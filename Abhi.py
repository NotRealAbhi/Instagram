import os
import re
import shutil
import instaloader
import zipfile
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Config import API_ID, API_HASH, BOT_TOKEN

bot = Client("insta_scraper_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

L = instaloader.Instaloader(
    dirname_pattern="downloads/{target}",
    download_video_thumbnails=False,
    save_metadata=False,
    post_metadata_txt_pattern=""
)

# ✅ Login to avoid 401 errors
# Option A: Username/Password (Enable this if you want)
# L.login("your_username", "your_password")

# Option B: Session login (Recommended)
# Make sure you saved a session file before with: instaloader --login=your_username
L.load_session_from_file("your_username")  # replace with your actual username

def get_username(text: str):
    match = re.search(r"(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)", text)
    if match:
        return match.group(1)
    parts = text.strip().split()
    return parts[0] if parts else None

def zip_directory(path, zip_name):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), path))
    zipf.close()

@bot.on_message(filters.command("start"))
async def start_handler(_, message: Message):
    await message.reply_text(
        "👋 Send an Instagram username or profile link to get profile info, stories, posts, reels, and more with download options!",
    )

@bot.on_message(filters.text & filters.private)
async def profile_handler(_, message: Message):
    try:
        username = get_username(message.text)
        if not username:
            return await message.reply_text("❌ Invalid username or link!")

        profile = instaloader.Profile.from_username(L.context, username)
        target_dir = f"downloads/{username}"
        L.download_profile(profile, profile_pic_only=True)

        caption = (
            f"👤 **{profile.full_name}**\n"
            f"🔗** Username**: `{profile.username}`\n"
            f"📌** Bio**: {profile.biography or 'N/A'}\n"
            f"📸** Posts**: {profile.mediacount}\n"
            f"👥 **Followers**: {profile.followers}\n"
            f"👣** Following**: {profile.followees}\n"
            f"🔒** Private**: {profile.is_private}\n"
            f"✔** Verified**: {profile.is_verified}\n"
        )

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Posts", callback_data=f"posts:{username}"),
             InlineKeyboardButton("🎞 Reels", callback_data=f"reels:{username}")],
            [InlineKeyboardButton("🖼 Profile Pic", callback_data=f"profile_pic:{username}"),
             InlineKeyboardButton("📂 Highlights", callback_data=f"highlights:{username}")],
            [InlineKeyboardButton("📖 Stories", callback_data=f"stories:{username}")],
            [InlineKeyboardButton("⬇️ Download All as ZIP", callback_data=f"zip:{username}")]
        ])

        pfp = os.path.join(target_dir, "profile_pic.jpg")
        if os.path.exists(pfp):
            await message.reply_photo(photo=pfp, caption=caption, reply_markup=markup)
        else:
            await message.reply_text(caption, reply_markup=markup)

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@bot.on_callback_query()
async def handle_callbacks(client, callback_query):
    try:
        data = callback_query.data
        query_type, username = data.split(":", 1)
        target_dir = f"downloads/{username}"
        profile = instaloader.Profile.from_username(L.context, username)

        if query_type == "profile_pic":
            pic_path = os.path.join(target_dir, "profile_pic.jpg")
            await callback_query.message.reply_photo(pic_path, caption="🖼 Profile Picture")

        elif query_type == "stories":
            L.download_stories(userids=[profile.userid])
            story_dir = os.path.join(target_dir, "stories")
            if os.path.exists(story_dir):
                for file in sorted(os.listdir(story_dir))[:10]:
                    f = os.path.join(story_dir, file)
                    if file.endswith(".mp4"):
                        await callback_query.message.reply_video(f)
                    else:
                        await callback_query.message.reply_photo(f)
            else:
                await callback_query.message.reply("No stories found.")

        elif query_type == "highlights":
            for highlight in profile.get_highlights():
                L.download_highlight(highlight)
                h_path = os.path.join(target_dir, highlight.title)
                if os.path.exists(h_path):
                    await callback_query.message.reply(f"🎯 Highlight: {highlight.title}")
                    for file in sorted(os.listdir(h_path))[:5]:
                        f = os.path.join(h_path, file)
                        if f.endswith(".mp4"):
                            await callback_query.message.reply_video(f)
                        else:
                            await callback_query.message.reply_photo(f)

        elif query_type == "posts":
            posts = profile.get_posts()
            for post in posts:
                L.download_post(post, target=profile.username)
            post_path = os.path.join(target_dir)
            media = []
            for file in sorted(os.listdir(post_path)):
                f = os.path.join(post_path, file)
                if f.endswith(".jpg"):
                    media.append(f)
            for i in range(0, len(media), 10):
                batch = media[i:i+10]
                await callback_query.message.reply_media_group([{"type": "photo", "media": m} for m in batch])

        elif query_type == "reels":
            reels = [post for post in profile.get_posts() if post.typename == "GraphVideo"]
            for reel in reels:
                L.download_post(reel, target=f"{username}_reels")
            r_path = os.path.join("downloads", f"{username}_reels")
            for file in sorted(os.listdir(r_path)):
                f = os.path.join(r_path, file)
                if f.endswith(".mp4"):
                    await callback_query.message.reply_video(f)

        elif query_type == "zip":
            zip_path = f"{target_dir}.zip"
            zip_directory(target_dir, zip_path)
            await callback_query.message.reply_document(zip_path, caption="📦 Download All Content as ZIP")

    except Exception as e:
        await callback_query.message.reply(f"❌ Error during `{query_type}`: {e}")

bot.run()
