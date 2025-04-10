import os
import re
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from Config import SESSION_ID


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/120.0.0.0 Safari/537.36"
    )
}


async def fetch_page(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=headers["User-Agent"])
        await context.add_cookies([{
            "name": "sessionid",
            "value": SESSION_ID,
            "domain": ".instagram.com",
            "path": "/"
        }])
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)
        html = await page.content()
        await browser.close()
        return html



async def fetch_media_links(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="text/javascript")
    media_links = []

    for script in scripts:
        if script.string and "display_url" in script.string:
            urls = re.findall(r'"display_url":"([^"]+)"', script.string)
            media_links.extend([url.replace("\\u0026", "&") for url in urls])

    return media_links


async def download_file(url: str, filename: str) -> str:
    ext = os.path.splitext(url.split("?")[0])[-1]
    if not ext.startswith("."):
        ext = ".jpg"

    path = f"{filename}{ext}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download. Status code: {response.status}")
                content = await response.read()
                if not content:
                    raise Exception("Downloaded content is empty.")
                with open(path, "wb") as f:
                    f.write(content)
        return path

    except Exception as e:
        print(f"[ERROR] download_file() failed: {e}")
        return None
