import asyncio
from pyrogram.types import InputMediaVideo
from Scraper import get_browser

async def send_reels(client, message, username):
    msg = await message.reply("🎥 Fetching Reels...")

    browser = await get_browser()
    page = await browser.new_page()
    await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

    try:
        # Click on the Reels tab (📹 button in profile)
        await page.wait_for_selector("svg[aria-label='Reels'], svg[aria-label='Reel']", timeout=15000)
        await page.locator("svg[aria-label='Reels'], svg[aria-label='Reel']").first.click()
        await asyncio.sleep(2)

        # Wait for reels to load
        await page.wait_for_selector("article a", timeout=10000)

        # Scroll and gather reel links
        reel_links = set()
        for _ in range(3):
            anchors = await page.locator("article a").all()
            for a in anchors:
                href = await a.get_attribute("href")
                if href and "/reel/" in href:
                    reel_links.add("https://www.instagram.com" + href)
            await page.mouse.wheel(0, 2000)
            await asyncio.sleep(2)

        media_list = []
        count = 0

        for link in list(reel_links)[:10]:  # Limit to 10 reels
            try:
                reel_page = await browser.new_page()
                await reel_page.goto(link, timeout=40000)
                await reel_page.wait_for_selector("video", timeout=10000)

                video_url = await reel_page.locator("video").first.get_attribute("src")
                if video_url:
                    media_list.append(InputMediaVideo(media=video_url))
                    count += 1

                await reel_page.close()

                # Send in batch of 10
                if len(media_list) >= 10:
                    await message.reply_media_group(media_list[:10])
                    media_list = media_list[10:]

            except Exception:
                continue

        if media_list:
            await message.reply_media_group(media_list)

        await msg.edit(f"✅ Fetched {count} Reels from `{username}`.")

    except Exception as e:
        await msg.edit(f"❌ Failed to fetch Reels.\n\nError: `{e}`")

    await browser.close()
