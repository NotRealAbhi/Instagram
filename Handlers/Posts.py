import asyncio
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from Scraper import get_browser

async def send_posts(client, message, username):
    msg = await message.reply("🔍 Fetching posts...")

    browser = await get_browser()
    page = await browser.new_page()
    await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

    try:
        # Wait for at least 1 post to load
        await page.wait_for_selector("article img, article video", timeout=15000)

        # Scroll and collect post links
        post_links = set()
        for _ in range(3):  # You can increase for more posts
            elements = await page.locator("article a").all()
            for el in elements:
                href = await el.get_attribute("href")
                if href and href.startswith("/p/"):
                    post_links.add("https://www.instagram.com" + href)
            await page.mouse.wheel(0, 2000)
            await asyncio.sleep(2)

        media_list = []
        count = 0

        for link in list(post_links)[:10]:  # Limit number of posts (10 for demo)
            try:
                post = await browser.new_page()
                await post.goto(link, timeout=40000)
                await post.wait_for_selector("article", timeout=10000)

                # Try image first
                img = await post.locator("article img").first.get_attribute("src")
                if img and "scontent" in img:
                    media_list.append(InputMediaPhoto(media=img))
                    count += 1
                    await post.close()
                    continue

                # If not image, try video
                vid = await post.locator("article video").first.get_attribute("src")
                if vid:
                    media_list.append(InputMediaVideo(media=vid))
                    count += 1
                await post.close()
            except Exception:
                continue

            # Send in batches of 10
            if len(media_list) >= 10:
                await message.reply_media_group(media_list[:10])
                media_list = media_list[10:]

        # Send remaining
        if media_list:
            await message.reply_media_group(media_list)

        await msg.edit(f"✅ Fetched {count} posts from `{username}`.")

    except Exception as e:
        await msg.edit(f"❌ Failed to fetch posts.\n\nError: `{e}`")

    await browser.close()
