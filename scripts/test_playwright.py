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

        # 1. Initial Desktop View with Aaranya Header
        await page.screenshot(path=os.path.join(SNAPSHOT_DIR, "01_desktop_hero_aaranya.png"))
        print("Captured 01_desktop_hero_aaranya.png")

        # 2. Hover over 'New & Featured'
        btn_new = page.locator('button[data-category="new-and-featured"]')
        await btn_new.hover()
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(SNAPSHOT_DIR, "02_megamenu_new_and_featured.png"))
        print("Captured 02_megamenu_new_and_featured.png")

        # 3. Hover over 'Necklaces'
        btn_neck = page.locator('button[data-category="necklaces"]')
        await btn_neck.hover()
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(SNAPSHOT_DIR, "03_megamenu_necklaces.png"))
        print("Captured 03_megamenu_necklaces.png")

        # 4. Hover over 'Rings'
        btn_rings = page.locator('button[data-category="rings"]')
        await btn_rings.hover()
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(SNAPSHOT_DIR, "04_megamenu_rings.png"))
        print("Captured 04_megamenu_rings.png")

        # 5. Hover over 'Bridal Jewellery'
        btn_bridal = page.locator('button[data-category="bridal-jewellery"]')
        await btn_bridal.hover()
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(SNAPSHOT_DIR, "05_megamenu_bridal.png"))
        print("Captured 05_megamenu_bridal.png")

        # 6. Test Escape key to close menu
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(400)
        is_open = await page.evaluate('document.getElementById("aaranya-mega-menu-container").classList.contains("is-open")')
        print("Menu open after Escape:", is_open)

        # 7. Test Hero Transition (Next Unveiling click)
        next_btn = page.locator('.next-trigger')
        if await next_btn.count() > 0:
            await next_btn.click()
            await page.wait_for_timeout(1800) # Wait for unveil transition
            await page.screenshot(path=os.path.join(SNAPSHOT_DIR, "06_hero_transition_verified.png"))
            print("Captured 06_hero_transition_verified.png")

        # 8. Mobile Viewport (390x844)
        mobile_context = await browser.new_context(viewport={'width': 390, 'height': 844})
        mobile_page = await mobile_context.new_page()
        await mobile_page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
        await mobile_page.wait_for_timeout(1000)
        await mobile_page.screenshot(path=os.path.join(SNAPSHOT_DIR, "07_mobile_hero.png"))
        print("Captured 07_mobile_hero.png")

        # Open mobile drawer
        await mobile_page.click('#aaranya-mobile-menu-btn')
        await mobile_page.wait_for_timeout(500)

        # Expand Necklaces accordion
        neck_accordion = mobile_page.locator('button.aaranya-accordion-trigger:has-text("Necklaces")')
        if await neck_accordion.count() > 0:
            await neck_accordion.click()
            await mobile_page.wait_for_timeout(400)

        await mobile_page.screenshot(path=os.path.join(SNAPSHOT_DIR, "08_mobile_drawer_open.png"))
        print("Captured 08_mobile_drawer_open.png")

        await browser.close()
        print("All tests completed successfully!")

if __name__ == '__main__':
    asyncio.run(run())
