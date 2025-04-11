from playwright.async_api import async_playwright
import asyncio

async def fetch_instagram_profile(username):
    profile = {
        "name": username,
        "bio": "",
        "profile_picture": "",
        "posts": [],
        "reels": [],
        "highlights": [],
        "stories": []
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                storage_state="auth/session.json"
            )
            page = await context.new_page()

            print(f"[🌐 Visiting] https://www.instagram.com/{username}/")
            await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

            await page.wait_for_selector("img[data-testid='user-avatar']", timeout=15000)
            profile_pic_elem = await page.query_selector("img[data-testid='user-avatar']")
            profile["profile_picture"] = await profile_pic_elem.get_attribute("src")

            name_elem = await page.query_selector("header h2")
            if name_elem:
                profile["name"] = await name_elem.inner_text()

            bio_elem = await page.query_selector("section div.x7a106z")
            if bio_elem:
                profile["bio"] = await bio_elem.inner_text()

            # Posts
            post_links = await page.query_selector_all("article a")
            for link in post_links:
                href = await link.get_attribute("href")
                if href and "/p/" in href:
                    profile["posts"].append(f"https://www.instagram.com{href}")

            # Reels
            print(f"[🎞️ Reels] Scraping reels tab...")
            await page.goto(f"https://www.instagram.com/{username}/reels/", timeout=60000)
            await page.wait_for_selector("article", timeout=15000)
            reels_links = await page.query_selector_all("article a")
            for link in reels_links:
                href = await link.get_attribute("href")
                if href and "/reel/" in href:
                    profile["reels"].append(f"https://www.instagram.com{href}")

            # Highlights
            print(f"[🧵 Highlights] Checking highlights...")
            await page.goto(f"https://www.instagram.com/stories/highlights/{username}/", timeout=60000)
            await asyncio.sleep(3)
            highlight_elems = await page.query_selector_all(".x1lliihq")
            for elem in highlight_elems:
                text = await elem.inner_text()
                if text:
                    profile["highlights"].append(text)

            # Stories - Hack via homepage
            print(f"[⏳ Stories] Attempting story check...")
            await page.goto("https://www.instagram.com", timeout=60000)
            await asyncio.sleep(3)
            story_elems = await page.query_selector_all("a[role='link']")
            for elem in story_elems:
                href = await elem.get_attribute("href")
                if href and username in href:
                    profile["stories"].append(f"https://www.instagram.com{href}")

            await browser.close()

    except Exception as e:
        print(f"[❌ ERROR]: {e}")
        return None

    return profile

# Debug/Test
if __name__ == "__main__":
    username = "cristiano"
    data = asyncio.run(fetch_instagram_profile(username))
    print(data)
