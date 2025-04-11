from playwright.async_api import async_playwright
from Config import SESSION_ID

async def get_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(storage_state={
        "cookies": [{
            "name": "sessionid",
            "value": SESSION_ID,
            "domain": ".instagram.com",
            "path": "/",
            "httpOnly": True,
            "secure": True
        }]
    })
    return context
