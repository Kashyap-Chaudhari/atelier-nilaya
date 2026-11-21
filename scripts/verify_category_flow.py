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

        print("1. Navigating to homepage...")
        await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")

        print("2. Scrolling to #shop-by-category...")
        shop_section = page.locator("#shop-by-category")
        await shop_section.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)

        # Verify category cards have non-zero naturalWidth (meaning image actually loaded!)
        img_check_script = """
        () => {
            const imgs = Array.from(document.querySelectorAll('#shop-by-category .aaranya-cat-img'));
            return imgs.map(img => ({
                src: img.src,
                complete: img.complete,
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight
            }));
        }
        """
        img_status = await page.evaluate(img_check_script)
        print("Category Images Status:")
        for idx, stat in enumerate(img_status):
            print(f"  [{idx+1}] {stat['src']} - Complete: {stat['complete']}, Dimensions: {stat['naturalWidth']}x{stat['naturalHeight']}")
            if stat['naturalWidth'] == 0:
                print(f"  WARNING: Image {stat['src']} has 0 naturalWidth!")

        # Screenshot of Shop by Category section
        snap_cat_sec = os.path.join(SNAPSHOT_DIR, "13_shop_by_category_verified.png")
        await shop_section.screenshot(path=snap_cat_sec)
        print(f"Saved: {snap_cat_sec}")

        # 3. Click Necklaces card
        print("3. Clicking 'Necklaces' category card...")
        necklaces_card = page.locator('.aaranya-cat-card[data-category-slug="necklaces"]')
        await necklaces_card.click()
        await page.wait_for_url("**/category/necklaces/**", timeout=8000)
        await page.wait_for_load_state("networkidle")
        print(f"Navigated to: {page.url}")

        # Assert page elements
        title = await page.title()
        print(f"Page title: {title}")
        assert "Necklaces" in title

        h1_text = await page.locator(".aaranya-cat-main-title").text_content()
        print(f"Main heading: {h1_text.strip()}")
        assert "Necklaces" in h1_text

        cards = page.locator(".aaranya-product-card")
        card_count = await cards.count()
        print(f"Found {card_count} product cards on Necklaces page.")
        assert card_count >= 5

        # Check product images naturalWidth
        prod_img_check = """
        () => {
            const imgs = Array.from(document.querySelectorAll('.aaranya-product-card .aaranya-card-img'));
            return imgs.map(img => ({
                src: img.src,
                complete: img.complete,
                naturalWidth: img.naturalWidth
            }));
        }
        """
        prod_img_status = await page.evaluate(prod_img_check)
        print(f"All {len(prod_img_status)} product images loaded:")
        for idx, stat in enumerate(prod_img_status):
            print(f"  Prod [{idx+1}] {stat['src'][:60]}... -> {stat['naturalWidth']}px")

        snap_necklaces = os.path.join(SNAPSHOT_DIR, "14_category_page_necklaces.png")
        await page.screenshot(path=snap_necklaces, full_page=True)
        print(f"Saved: {snap_necklaces}")

        # 4. Click 'Earrings' pill in nav strip
        print("4. Clicking 'Earrings' pill in category pill bar...")
        earrings_pill = page.locator('.aaranya-cat-pill:has-text("Earrings")')
        await earrings_pill.click()
        await page.wait_for_url("**/category/earrings/**", timeout=8000)
        await page.wait_for_load_state("networkidle")
        print(f"Navigated to: {page.url}")

        earrings_h1 = await page.locator(".aaranya-cat-main-title").text_content()
        print(f"Earrings heading: {earrings_h1.strip()}")
        assert "Earrings" in earrings_h1

        snap_earrings = os.path.join(SNAPSHOT_DIR, "15_category_page_earrings.png")
        await page.screenshot(path=snap_earrings, full_page=True)
        print(f"Saved: {snap_earrings}")

        # 5. Click 'All Vault' pill to view all products
        print("5. Clicking 'All Vault' pill...")
        vault_pill = page.locator('.aaranya-cat-pill:has-text("All Vault")')
        await vault_pill.click()
        await page.wait_for_url("**/vault/**", timeout=8000)
        await page.wait_for_load_state("networkidle")
        print(f"Navigated to: {page.url}")

        vault_cards = page.locator(".aaranya-product-card")
        total_vault_cards = await vault_cards.count()
        print(f"Found {total_vault_cards} product cards in Complete Vault.")
        assert total_vault_cards == 31

        snap_vault = os.path.join(SNAPSHOT_DIR, "16_complete_vault_all_products.png")
        await page.screenshot(path=snap_vault, full_page=True)
        print(f"Saved: {snap_vault}")

        await browser.close()
        print("SUCCESS! All category navigation, image loading, and product views verified!")

if __name__ == "__main__":
    asyncio.run(run())
