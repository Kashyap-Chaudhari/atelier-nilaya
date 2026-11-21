import os
import asyncio
from playwright.async_api import async_playwright

SNAPSHOT_DIR = os.path.join(os.getcwd(), 'browser_snapshots')
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        print("Navigating to http://127.0.0.1:8000/ ...")
        await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Scroll to Shop by Category section
        cat_section = page.locator('#shop-by-category')
        await cat_section.scroll_into_view_if_needed()
        await page.wait_for_timeout(600)

        # 1. Capture Desktop View of Shop by Category Section
        await page.screenshot(path=os.path.join(SNAPSHOT_DIR, "09_shop_by_category_desktop.png"))
        print("Captured 09_shop_by_category_desktop.png")

        # 2. Hover over 'Necklaces' card
        neck_card = page.locator('.aaranya-cat-card[data-category-target="necklaces"]')
        await neck_card.hover()
        await page.wait_for_timeout(400)
        await page.screenshot(path=os.path.join(SNAPSHOT_DIR, "10_shop_by_category_hover.png"))
        print("Captured 10_shop_by_category_hover.png")

        # 3. Click Next Arrow
        next_btn = page.locator('#cat-next-btn')
        await next_btn.click()
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(SNAPSHOT_DIR, "11_shop_by_category_scrolled.png"))
        print("Captured 11_shop_by_category_scrolled.png")

        # 4. Mobile Viewport (390x844)
        mobile_context = await browser.new_context(viewport={'width': 390, 'height': 844})
        mobile_page = await mobile_context.new_page()
        await mobile_page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        await mobile_page.wait_for_timeout(1000)

        mobile_cat = mobile_page.locator('#shop-by-category')
        await mobile_cat.scroll_into_view_if_needed()
        await mobile_page.wait_for_timeout(600)

        await mobile_page.screenshot(path=os.path.join(SNAPSHOT_DIR, "12_shop_by_category_mobile.png"))
        print("Captured 12_shop_by_category_mobile.png")

        await browser.close()
        print("All Category Section tests completed successfully!")

if __name__ == '__main__':
    asyncio.run(run())
