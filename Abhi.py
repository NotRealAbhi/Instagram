import os
import re
import shutil
import instaloader
import zipfile
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Config import API_ID, API_HASH, BOT_TOKEN

bot = Client("insta_scraper_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

sessionid = "70251829033%3AWxEGqggNOdfsNJ%3A13%3AAYcKvGI0IPZ6F1PFMA3Oh0dp0jw-xf1OBp2E_o515g"  # Replace with your real Instagram sessionid
L = instaloader.Instaloader()
L.context._session.cookies.set("sessionid", sessionid)

# Verify login
try:
    profile = instaloader.Profile.from_username(L.context, "instagram")  # dummy check
    print("✅ Logged in successfully.")
except Exception as e:
    print("❌ Login failed:", e)

def get_username(text: str):
    match = re.search(r"(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9_.]+)", text)
    return match.group(1) if match else text.strip().split()[0]

def zip_directory(path, zip_name):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), path))
    zipf.close()

@bot.on_message(filters.command("start"))
async def start_handler(_, message: Message):
    await message.reply_text("👋 Send an Instagram username or profile link to get profile info with media download options.")

@bot.on_message(filters.text & filters.private)
async def profile_handler(_, message: Message):
    try:
        username = get_username(message.text)
        profile = instaloader.Profile.from_username(L.context, username)
        target_dir = f"downloads/{username}"
        os.makedirs(target_dir, exist_ok=True)
        L.download_profile(profile, profile_pic_only=True)


        caption = (
            f"👤 **{profile.full_name}**\n"
            f"🔗 **Username**: `{profile.username}`\n"
            f"📌 **Bio**: {profile.biography or 'N/A'}\n"
            f"📸 **Posts**: {profile.mediacount}\n"
            f"👥 **Followers**: {profile.followers}\n"
            f"👣 **Following**: {profile.followees}\n"
            f"🔒 **Private**: {profile.is_private}\n"
            f"✔️ **Verified**: {profile.is_verified}"
        )

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Posts", callback_data=f"posts:{username}"),
             InlineKeyboardButton("🎞 Reels", callback_data=f"reels:{username}")],
            [InlineKeyboardButton("🖼 Profile Pic", callback_data=f"profile_pic:{username}"),
             InlineKeyboardButton("📖 Stories", callback_data=f"stories:{username}")],
            [InlineKeyboardButton("⬇️ Download ZIP", callback_data=f"zip:{username}")]
        ])

        pfp = os.path.join(target_dir, f"{username}_profile_pic.jpg")
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
        os.makedirs(target_dir, exist_ok=True)
        profile = instaloader.Profile.from_username(L.context, username)

        if query_type == "profile_pic":
            pic_path = os.path.join(target_dir, f"{username}_profile_pic.jpg")
            if os.path.exists(pic_path):
                await callback_query.message.reply_photo(pic_path, caption="🖼 Profile Picture")
            else:
                await callback_query.message.reply("❌ Profile picture not found.")

        elif query_type == "stories":
            stories_path = os.path.join(target_dir, "stories")
            shutil.rmtree(stories_path, ignore_errors=True)
            L.download_stories(userids=[profile.userid], filename_target=stories_path)
            if os.path.exists(stories_path):
                for file in sorted(os.listdir(stories_path))[:10]:
                    f = os.path.join(stories_path, file)
                    if file.endswith(".mp4"):
                        await callback_query.message.reply_video(f)
                    elif file.endswith(".jpg"):
                        await callback_query.message.reply_photo(f)
            else:
                await callback_query.message.reply("No stories available.")

        elif query_type == "posts":
            posts = profile.get_posts()
            post_dir = os.path.join(target_dir, "posts")
            os.makedirs(post_dir, exist_ok=True)
            count = 0
            for post in posts:
                if count >= 5:  # Limit to 5 for quick demo
                    break
                L.download_post(post, target=post_dir)
                count += 1

            media = [os.path.join(post_dir, f) for f in os.listdir(post_dir) if f.endswith(".jpg")]
            for i in range(0, len(media), 10):
                batch = media[i:i + 10]
                await callback_query.message.reply_media_group([{"type": "photo", "media": m} for m in batch])

        elif query_type == "reels":
            reels_dir = os.path.join(target_dir, "reels")
            os.makedirs(reels_dir, exist_ok=True)
            for post in profile.get_posts():
                if post.typename == "GraphVideo":
                    L.download_post(post, target=reels_dir)
            reels = [os.path.join(reels_dir, f) for f in os.listdir(reels_dir) if f.endswith(".mp4")]
            for r in reels:
                await callback_query.message.reply_video(r)

        elif query_type == "zip":
            zip_path = f"{target_dir}.zip"
            zip_directory(target_dir, zip_path)
            await callback_query.message.reply_document(zip_path, caption="📦 Downloaded ZIP")

    except Exception as e:
        await callback_query.message.reply(f"❌ Error during `{query_type}`: {e}")

bot.run()
