import os
import asyncio
from playwright.async_api import async_playwright
from Config import SESSION_ID

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

async def fetch_page(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                storage_state={"cookies": [{"name": "sessionid", "value": SESSION_ID, "domain": ".instagram.com"}]},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(4000)
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        print(f"[scraper.py] Error in fetch_page: {e}")
        return ""

async def download_file(url: str, filename: str) -> str:
    if not url or not filename:
        print("[scraper.py] Invalid URL or filename passed to download_file.")
        return None

    try:
        import aiohttp

        path = os.path.join(DOWNLOADS_DIR, filename)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(path, "wb") as f:
                        f.write(await resp.read())
                    return path
                else:
                    print(f"[scraper.py] Failed to download file, status code: {resp.status}")
                    return None
    except Exception as e:
        print(f"[scraper.py] Exception in download_file: {e}")
        return None
