import asyncio
import os
import sys
from playwright.async_api import async_playwright

SNAPSHOT_DIR = r"C:\Users\hi\.gemini\antigravity\brain\f6fd8ec0-0b1d-46c1-8a61-9162ce04f9f5\browser_snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

async def run():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(channel="chrome", headless=True)
        except Exception:
            browser = await p.chromium.launch(channel="msedge", headless=True)
            
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("1. Loading homepage...")
        await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")

        # 2. Check Shop by Category images
        print("2. Checking Shop by Category section images...")
        shop_section = page.locator("#shop-by-category")
        await shop_section.scroll_into_view_if_needed()
        await page.wait_for_timeout(800)

        img_stats = await page.evaluate("""
        () => {
            const imgs = Array.from(document.querySelectorAll('#shop-by-category .aaranya-cat-img'));
            return imgs.map(img => ({
                src: img.src,
                complete: img.complete,
                width: img.naturalWidth,
                height: img.naturalHeight
            }));
        }
        """)
        for idx, stat in enumerate(img_stats):
            print(f"  Category Img [{idx+1}]: {stat['width']}x{stat['height']} (complete={stat['complete']}) -> {stat['src'][-30:]}")
            assert stat['width'] > 0, f"Image failed to load: {stat['src']}"

        cat_shot = os.path.join(SNAPSHOT_DIR, "21_verified_shop_by_category_cards.png")
        await shop_section.screenshot(path=cat_shot)
        print(f"Saved: {cat_shot}")

        # Scroll back up to test Mega Menus
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        # 3. Test Mega Menu Panels & Thumbnails
        panels_to_test = [
            ("earrings", "Earrings", "22_mega_menu_earrings_authentic.png"),
            ("rings", "Rings", "23_mega_menu_rings_authentic.png"),
            ("bangles", "Bangles", "24_mega_menu_bangles_authentic.png"),
            ("bridal-jewellery", "Bridal Jewellery", "25_mega_menu_bridal_authentic.png"),
        ]

        for cat_key, cat_name, filename in panels_to_test:
            print(f"Testing Mega Menu: {cat_name}...")
            btn = page.locator(f'.aaranya-nav-btn[data-category="{cat_key}"]')
            await btn.hover()
            await page.wait_for_timeout(500)
            
            panel = page.locator(f'.aaranya-menu-panel[data-panel="{cat_key}"]')
            await panel.wait_for(state="visible", timeout=3000)
            
            # Check thumbnails in panel
            thumb_stats = await page.evaluate(f"""
            () => {{
                const panel = document.querySelector('.aaranya-menu-panel[data-panel="{cat_key}"]');
                const imgs = Array.from(panel.querySelectorAll('.aaranya-thumb-img'));
                return imgs.map(img => ({{
                    src: img.src.split('/').pop(),
                    width: img.naturalWidth,
                    height: img.naturalHeight
                }}));
            }}
            """)
            print(f"  {cat_name} thumbnails: {len(thumb_stats)} found")
            for t in thumb_stats:
                assert t['width'] > 0, f"Broken thumbnail {t['src']} in {cat_name}"
            
            snap_path = os.path.join(SNAPSHOT_DIR, filename)
            # Screenshot of the mega menu overlay
            menu_container = page.locator("#aaranya-mega-menu-container")
            await menu_container.screenshot(path=snap_path)
            print(f"  Saved mega menu snapshot: {snap_path}")

        # 4. Click a Subcategory Link (e.g. Chandbalis in Earrings)
        print("4. Testing click navigation from Mega Menu to Category Page...")
        earrings_btn = page.locator('.aaranya-nav-btn[data-category="earrings"]')
        await earrings_btn.hover()
        await page.wait_for_timeout(400)

        chandbalis_link = page.locator('.aaranya-menu-panel[data-panel="earrings"] a[href*="chandbali"]')
        await chandbalis_link.click()
        await page.wait_for_url("**/category/earrings/**", timeout=8000)
        await page.wait_for_load_state("networkidle")
        print(f"Navigated to: {page.url}")
        assert "sub=chandbali" in page.url or "earrings" in page.url

        # Check page products
        product_cards = page.locator(".aaranya-product-card")
        p_count = await product_cards.count()
        print(f"Product cards on filtered page: {p_count}")
        assert p_count > 0, "No product cards displayed!"

        snap_filtered = os.path.join(SNAPSHOT_DIR, "26_filtered_chandbalis_page.png")
        await page.screenshot(path=snap_filtered)
        print(f"Saved: {snap_filtered}")

        # 5. Check Vault page breadcrumbs & title
        print("5. Testing /vault/ layout & breadcrumbs...")
        await page.goto("http://127.0.0.1:8000/vault/", wait_until="networkidle")
        vault_title = await page.locator(".aaranya-cat-main-title").text_content()
        print(f"Vault title: {vault_title.strip()}")
        assert "All Jewellery Artworks" in vault_title or "Vault" in vault_title

        snap_vault = os.path.join(SNAPSHOT_DIR, "27_vault_redesigned_layout.png")
        await page.screenshot(path=snap_vault)
        print(f"Saved: {snap_vault}")

        await browser.close()
        print("\nALL VISUAL AND INTERACTION TESTS PASSED BEAUTIFULLY!")

if __name__ == '__main__':
    asyncio.run(run())
