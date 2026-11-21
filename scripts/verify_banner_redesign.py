import asyncio
import os
from playwright.async_api import async_playwright

SNAPSHOT_DIR = r"C:\Users\hi\.gemini\antigravity\brain\f6fd8ec0-0b1d-46c1-8a61-9162ce04f9f5\browser_snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

async def run():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            browser = await p.chromium.launch(channel="msedge", headless=True)

        # 1. Desktop Test for /vault/
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("1. Opening /vault/ ...")
        await page.goto("http://127.0.0.1:8000/vault/", wait_until="networkidle")
        await page.wait_for_timeout(800)

        # Capture specifically the banner
        banner = page.locator(".aaranya-cat-hero-banner")
        banner_vault_snap = os.path.join(SNAPSHOT_DIR, "17_redesigned_banner_vault.png")
        await banner.screenshot(path=banner_vault_snap)
        print(f"Saved: {banner_vault_snap}")

        # Capture full page view of vault top
        vault_top_snap = os.path.join(SNAPSHOT_DIR, "18_redesigned_vault_top_desktop.png")
        await page.screenshot(path=vault_top_snap)
        print(f"Saved: {vault_top_snap}")

        # 2. Desktop Test for /category/necklaces/
        print("2. Opening /category/necklaces/ ...")
        await page.goto("http://127.0.0.1:8000/category/necklaces/", wait_until="networkidle")
        await page.wait_for_timeout(800)

        banner_neck_snap = os.path.join(SNAPSHOT_DIR, "19_redesigned_banner_necklaces.png")
        await banner.screenshot(path=banner_neck_snap)
        print(f"Saved: {banner_neck_snap}")

        # 3. Mobile Viewport Test (390x844)
        print("3. Testing mobile view on /vault/ ...")
        mobile_context = await browser.new_context(viewport={"width": 390, "height": 844})
        mobile_page = await mobile_context.new_page()
        await mobile_page.goto("http://127.0.0.1:8000/vault/", wait_until="networkidle")
        await mobile_page.wait_for_timeout(800)

        mobile_banner = mobile_page.locator(".aaranya-cat-hero-banner")
        mobile_banner_snap = os.path.join(SNAPSHOT_DIR, "20_redesigned_banner_mobile.png")
        await mobile_banner.screenshot(path=mobile_banner_snap)
        print(f"Saved: {mobile_banner_snap}")

        await browser.close()
        print("Completed banner redesign visual verification!")

if __name__ == "__main__":
    asyncio.run(run())
