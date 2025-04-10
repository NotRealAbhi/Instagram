import asyncio
import os
import re
import shutil
import uuid
from playwright.async_api import async_playwright
from Config import SESSION_ID

BASE_DIR = "downloads"

def clean_dir(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

def sanitize_filename(text: str):
    return re.sub(r'[\\/*?:"<>|]', "", text)

async def scrape_instagram(username: str):
    user_dir = os.path.join(BASE_DIR, username)
    clean_dir(user_dir)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            storage_state={
                "cookies": [
                    {
                        "name": "sessionid",
                        "value": SESSION_ID,
                        "domain": ".instagram.com",
                        "path": "/",
                        "httpOnly": True,
                        "secure": True,
                        "sameSite": "Lax"
                    }
                ]
            }
        )
        page = await context.new_page()
        await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)

        await page.wait_for_selector("img", timeout=10000)

        # Profile Info
        full_name = await page.locator('header section h1').text_content()
        bio = await page.locator('header section > div > h1 + div').text_content() or "No Bio"
        profile_pic_url = await page.locator("img").first.get_attribute("src")

        # Save Profile Pic
        profile_pic_path = os.path.join(user_dir, "profile_pic.jpg")
        await download_file(page, profile_pic_url, profile_pic_path)

        await browser.close()

        return {
            "username": username,
            "full_name": full_name.strip() if full_name else username,
            "bio": bio.strip(),
            "profile_pic": profile_pic_path,
            "dir": user_dir
        }

async def fetch_page(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)  # Give time for JS to render
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        print(f"❌ Error fetching page: {e}")
        return None


async def download_file(page, url, path):
    try:
        async with page.expect_download() as download_info:
            await page.evaluate(f"""() => {{
                const a = document.createElement('a');
                a.href = '{url}';
                a.download = '';
                document.body.appendChild(a);
                a.click();
            }}""")
        download = await download_info.value
        await download.save_as(path)
    except:
        # fallback if expect_download fails (like image urls)
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(path, 'wb') as f:
                        f.write(await resp.read())

async def get_stories(username: str, user_dir: str):
    # Future scope: fetch stories via JSON endpoints (if Playwright supports logged-in sessions)
    # Placeholder if you want to implement via headless screen scraping.
    pass

# Optional helper to run directly for testing
if __name__ == "__main__":
    import sys
    username = sys.argv[1] if len(sys.argv) > 1 else "instagram"
    data = asyncio.run(scrape_instagram(username))
    print(data)
  
