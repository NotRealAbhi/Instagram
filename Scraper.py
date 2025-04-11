import asyncio
from playwright.async_api import async_playwright
from Config import SESSION_ID


async def fetch_instagram_profile(username: str):
    url = f"https://www.instagram.com/{username}/"
    profile_data = {
        "name": username,
        "bio": "No bio found.",
        "profile_picture": None,
        "reels": [],
        "posts": [],
        "stories": [],
        "highlights": []
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            # Apply session cookie
            await context.add_cookies([{
                'name': 'sessionid',
                'value': SESSION_ID,
                'domain': '.instagram.com',
                'path': '/'
            }])

            page = await context.new_page()
            print(f"[🌐 Visiting] {url}")
            await page.goto(url, timeout=60000)

            # Wait for profile picture (fallback selector if old fails)
            try:
                await page.wait_for_selector("img[alt*='profile picture'], img[data-testid='user-avatar']", timeout=10000)
                profile_pic = await page.query_selector("img[alt*='profile picture'], img[data-testid='user-avatar']")
                profile_data["profile_picture"] = await profile_pic.get_attribute("src")
            except:
                print("⚠️ Profile picture not found.")

            # Name and Bio
            try:
                name_el = await page.query_selector("header h2, header h1")
                profile_data["name"] = await name_el.inner_text() if name_el else username
            except:
                pass

            try:
                bio_el = await page.query_selector("div._aa_c span")
                profile_data["bio"] = await bio_el.inner_text() if bio_el else "No bio found."
            except:
                pass

            # Posts
            try:
                posts = await page.query_selector_all("article div img")
                for post in posts[:10]:
                    src = await post.get_attribute("src")
                    if src:
                        profile_data["posts"].append(src)
            except:
                pass

            # Reels (navigate to reels tab)
            try:
                reels_tab = await page.query_selector("a[href$='/reels/']")
                if reels_tab:
                    await reels_tab.click()
                    await page.wait_for_timeout(3000)
                    reels = await page.query_selector_all("article video")
                    for reel in reels[:5]:
                        src = await reel.get_attribute("src")
                        if src:
                            profile_data["reels"].append(src)
            except:
                print("⚠️ Reels tab not found or empty.")

            # Highlights & Stories (optional, dynamic)
            # These require more effort or Instagram Graph API (not via scraping)

            await browser.close()

    except Exception as e:
        print(f"[❌ ERROR]: {e}")
        return None

    return profile_data


# For testing
if __name__ == "__main__":
    username = input("Enter Instagram username: ")
    result = asyncio.run(fetch_instagram_profile(username))
    print(result)
    
