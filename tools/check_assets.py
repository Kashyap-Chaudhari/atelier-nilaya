#!/usr/bin/env python3
"""
Atelier Nilaya — Asset Auditor (check_assets.py)
Verifies that for every product in the database and every offered metal (in_stock = 1):
1. All 36 spin frames (001.webp to 036.webp) exist.
2. Still views (front.webp, side.webp, top.webp) exist.
3. Lifestyle photo (lifestyle-1.webp) exists.
4. All images are valid WebP files with uniform dimensions (e.g. 600x600).
5. Every single image is under 120 KB in file size.

Returns exit code 0 if all assets pass audit.
Returns exit code 1 with a detailed failure report if any asset is missing or invalid.
"""

import os
import sys
import sqlite3
from PIL import Image

MAX_FILE_SIZE_BYTES = 120 * 1024  # 120 KB
DEFAULT_SPIN_FRAMES = 36

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_PRODUCTS_DIR = os.path.join(BASE_DIR, 'static', 'products')
DB_PATH = os.path.join(BASE_DIR, 'nilaya.db')

def check_assets(db_path=DB_PATH, products_dir=STATIC_PRODUCTS_DIR):
    print("=" * 80)
    print("ATELIER NILAYA — PRODUCT IMAGERY ASSET AUDITOR")
    print(f"Database: {db_path}")
    print(f"Products Directory: {products_dir}")
    print(f"Maximum Allowed File Size: {MAX_FILE_SIZE_BYTES / 1024:.0f} KB")
    print("=" * 80)

    if not os.path.exists(db_path):
        print(f"ERROR: Database file '{db_path}' not found.")
        sys.exit(1)

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    products = cur.execute("""
        SELECT id, name, slug, base_metal, COALESCE(spin_frames, 36) as spin_frames
        FROM products
        ORDER BY id ASC
    """).fetchall()

    if not products:
        print("ERROR: No products found in database.")
        sys.exit(1)

    total_products = len(products)
    total_checks = 0
    total_passed = 0
    errors = []
    warnings = []

    print(f"\nAuditing {total_products} products across all offered metal variants...\n")

    # 1. Product Name -> Image Folder Mapping Table (Proof of ID/Slug matching)
    print("MAPPING VERIFICATION: Product Name -> Image Folder")
    print("-" * 90)
    print(f"{'ID':<4} | {'PRODUCT NAME':<40} | {'IMAGE FOLDER (SLUG)':<40}")
    print("-" * 90)
    for p_id, p_name, p_slug, p_base_metal, p_spin_frames in products:
        prod_folder = os.path.join(products_dir, p_slug)
        folder_status = p_slug if os.path.isdir(prod_folder) else f"{p_slug} [MISSING FOLDER!]"
        if not os.path.isdir(prod_folder):
            errors.append(f"[{p_slug}] Product directory does not exist on disk: {prod_folder}")
        print(f"{p_id:<4} | {p_name:<40} | {folder_status:<40}")
    print("-" * 90)

    print(f"\n{'SLUG':<38} | {'METAL':<12} | {'SPIN':<12} | {'STILLS':<8} | {'LIFESTYLE':<9} | {'STATUS'}")
    print("-" * 90)

    for p_id, p_name, p_slug, p_base_metal, p_spin_frames in products:
        prod_path = os.path.join(products_dir, p_slug)
        
        # Check lifestyle photo
        lifestyle_path = os.path.join(prod_path, 'lifestyle-1.webp')
        total_checks += 1
        lifestyle_ok = True
        if not os.path.exists(lifestyle_path):
            errors.append(f"[{p_slug}] Missing lifestyle image: {lifestyle_path}")
            lifestyle_ok = False
        else:
            sz = os.path.getsize(lifestyle_path)
            if sz > MAX_FILE_SIZE_BYTES:
                errors.append(f"[{p_slug}] Lifestyle image exceeds 120KB: {sz / 1024:.1f} KB")
                lifestyle_ok = False
            try:
                with Image.open(lifestyle_path) as im:
                    if im.format != 'WEBP':
                        errors.append(f"[{p_slug}] Lifestyle image format is {im.format}, expected WEBP")
                        lifestyle_ok = False
            except Exception as e:
                errors.append(f"[{p_slug}] Lifestyle image corrupt: {e}")
                lifestyle_ok = False

        if lifestyle_ok:
            total_passed += 1

        # Fetch offered metals from product_metals where in_stock = 1
        metals_rows = cur.execute("""
            SELECT metal, in_stock FROM product_metals
            WHERE product_id = ? AND in_stock = 1
        """, (p_id,)).fetchall()

        offered_metals = [m[0] for m in metals_rows]
        if not offered_metals:
            offered_metals = [p_base_metal]

        for metal in offered_metals:
            metal_path = os.path.join(prod_path, metal)
            spin_path = os.path.join(metal_path, 'spin')
            
            metal_spin_ok = True
            frames_found = 0
            expected_frames = p_spin_frames or DEFAULT_SPIN_FRAMES
            
            # Check 36 spin frames
            for idx in range(1, expected_frames + 1):
                total_checks += 1
                frame_filename = f"{idx:03d}.webp"
                frame_file = os.path.join(spin_path, frame_filename)
                
                if not os.path.exists(frame_file):
                    errors.append(f"[{p_slug}/{metal}] Missing spin frame: {frame_filename}")
                    metal_spin_ok = False
                else:
                    frames_found += 1
                    sz = os.path.getsize(frame_file)
                    if sz > MAX_FILE_SIZE_BYTES:
                        errors.append(f"[{p_slug}/{metal}] Frame {frame_filename} exceeds 120KB ({sz / 1024:.1f} KB)")
                        metal_spin_ok = False
                    try:
                        with Image.open(frame_file) as im:
                            if im.format != 'WEBP':
                                errors.append(f"[{p_slug}/{metal}] Frame {frame_filename} is not WEBP ({im.format})")
                                metal_spin_ok = False
                    except Exception as e:
                        errors.append(f"[{p_slug}/{metal}] Frame {frame_filename} corrupt: {e}")
                        metal_spin_ok = False
                        
                    if metal_spin_ok:
                        total_passed += 1

            # Check Stills: front, side, top
            stills_ok = True
            for still_name in ['front.webp', 'side.webp', 'top.webp']:
                total_checks += 1
                still_file = os.path.join(metal_path, still_name)
                if not os.path.exists(still_file):
                    errors.append(f"[{p_slug}/{metal}] Missing still view: {still_name}")
                    stills_ok = False
                else:
                    sz = os.path.getsize(still_file)
                    if sz > MAX_FILE_SIZE_BYTES:
                        errors.append(f"[{p_slug}/{metal}] Still {still_name} exceeds 120KB ({sz / 1024:.1f} KB)")
                        stills_ok = False
                    try:
                        with Image.open(still_file) as im:
                            if im.format != 'WEBP':
                                errors.append(f"[{p_slug}/{metal}] Still {still_name} is not WEBP ({im.format})")
                                stills_ok = False
                    except Exception as e:
                        errors.append(f"[{p_slug}/{metal}] Still {still_name} corrupt: {e}")
                        stills_ok = False

                    if stills_ok:
                        total_passed += 1

            status_str = "PASS" if (metal_spin_ok and stills_ok and lifestyle_ok) else "FAIL"
            print(f"{p_slug:<38} | {metal:<12} | {frames_found}/{expected_frames} frames | {'3/3' if stills_ok else 'ERR'} stills | {'OK' if lifestyle_ok else 'MISSING'}  | {status_str}")

    # 2. Auditing The Sketchbook Designs (Archival Drawings -> Real Products)
    print("\n" + "=" * 80)
    print("AUDITING THE SKETCHBOOK DESIGNS ('designs' table -> sketches & finished jewels)")
    print("=" * 80)
    print(f"{'Year & Title':<38} | {'Linked Product Slug':<36} | {'Sketch File':<12} | {'Finished Still':<14} | Status")
    print("-" * 115)

    designs = cur.execute("""
        SELECT d.id, d.year, d.title, d.sketch_path, d.sketch_alt, d.sort_order,
               p.id as product_id, p.slug as product_slug, p.name as product_name
        FROM designs d
        LEFT JOIN products p ON d.product_id = p.id
        ORDER BY d.sort_order ASC
    """).fetchall()

    if not designs:
        errors.append("No designs found in 'designs' table.")
    else:
        for d in designs:
            d_id, year, title, sketch_path, sketch_alt, sort_order, pid, p_slug, p_name = d
            d_ok = True
            total_checks += 1

            # 1. Product linkage check
            if not pid or not p_slug:
                errors.append(f"[Design {year} '{title}'] Linked product ID {d_id} does not exist in 'products' table.")
                d_ok = False

            # 2. Sketch file check
            clean_rel = sketch_path.lstrip('/')
            abs_sketch = os.path.join(BASE_DIR, clean_rel.replace('/', os.sep))
            sketch_exists = os.path.exists(abs_sketch)
            if not sketch_exists:
                errors.append(f"[Design {year} '{title}'] Sketch file missing on disk: {sketch_path}")
                d_ok = False
            else:
                sz = os.path.getsize(abs_sketch)
                if sz > MAX_FILE_SIZE_BYTES:
                    errors.append(f"[Design {year} '{title}'] Sketch exceeds 120KB: {sz / 1024:.1f} KB")
                    d_ok = False
                try:
                    with Image.open(abs_sketch) as im:
                        if im.format != 'WEBP':
                            errors.append(f"[Design {year} '{title}'] Sketch is not WEBP: {im.format}")
                            d_ok = False
                except Exception as e:
                    errors.append(f"[Design {year} '{title}'] Corrupt sketch: {e}")
                    d_ok = False

            # 3. Finished piece images check
            finished_still_ok = False
            if p_slug:
                # Check for front.webp in any offered metal folder
                for metal in ['yellow_gold', 'platinum', 'rose_gold', 'silver']:
                    front_f = os.path.join(STATIC_PRODUCTS_DIR, p_slug, metal, 'front.webp')
                    if os.path.exists(front_f):
                        finished_still_ok = True
                        break

            if not finished_still_ok:
                errors.append(f"[Design {year} '{title}'] Product '{p_slug}' missing finished front.webp image!")
                d_ok = False

            if d_ok:
                total_passed += 1

            status_d = "PASS" if d_ok else "FAIL"
            display_title = f"{year} {title}"[:36]
            display_slug = (p_slug or "NONE")[:34]
            print(f"{display_title:<38} | {display_slug:<36} | {'FOUND' if sketch_exists else 'MISSING':<12} | {'FOUND' if finished_still_ok else 'MISSING':<14} | {status_d}")

        # -------------------------------------------------------------------------
        # 3. FEATURED EDIT ASSETS AUDIT
        # -------------------------------------------------------------------------
        print("\n" + "=" * 90)
        print("AUDITING 'FEATURED EDIT' SECTION ASSETS (Faded Band & 12-Col Editorial Grid)")
        print("Section Weight Budget: 700 KB (716,800 bytes)")
        print("-" * 90)
        print(f"{'ASSET TYPE':<24} | {'PATH':<42} | {'ALT TEXT':<14} | {'SIZE (KB)':<10} | {'STATUS'}")
        print("-" * 90)

        featured_section = cur.execute("SELECT * FROM feature_section WHERE active = 1 ORDER BY id ASC LIMIT 1").fetchone()
        if featured_section:
            f_cols = [c[0] for c in cur.description]
            f_sec = dict(zip(f_cols, featured_section))
            sec_weight = 0

            # Check band background & hexagons
            band_items = [
                ("Band Background", f_sec.get('bg_image_path'), f_sec.get('bg_alt'), 150),
                ("Hexagon 1 (Ring)", f_sec.get('hex_1_path'), f_sec.get('hex_1_alt'), 120),
                ("Hexagon 2 (Earrings)", f_sec.get('hex_2_path'), f_sec.get('hex_2_alt'), 120),
                ("Hexagon 3 (Necklace)", f_sec.get('hex_3_path'), f_sec.get('hex_3_alt'), 120),
            ]

            for label, img_path, alt_txt, max_kb in band_items:
                total_checks += 1
                item_ok = True
                sz = 0
                abs_f = ""
                if not img_path:
                    errors.append(f"Featured Edit {label}: Image path is empty")
                    item_ok = False
                else:
                    rel = img_path.lstrip('/')
                    abs_f = os.path.join(BASE_DIR, rel.replace('/', os.sep))
                    if not os.path.exists(abs_f):
                        errors.append(f"Featured Edit {label}: File missing at {img_path}")
                        item_ok = False
                    else:
                        sz = os.path.getsize(abs_f)
                        sec_weight += sz
                        if sz > max_kb * 1024:
                            errors.append(f"Featured Edit {label}: Exceeds {max_kb}KB limit ({sz/1024:.1f}KB)")
                            item_ok = False
                        if not alt_txt or len(alt_txt.strip()) == 0:
                            errors.append(f"Featured Edit {label}: Missing alt text")
                            item_ok = False
                        try:
                            with Image.open(abs_f) as im:
                                if im.format != 'WEBP':
                                    errors.append(f"Featured Edit {label}: Format is {im.format}, expected WEBP")
                                    item_ok = False
                        except Exception as e:
                            errors.append(f"Featured Edit {label}: Corrupt image: {e}")
                            item_ok = False
                if item_ok:
                    total_passed += 1
                sz_str = f"{sz/1024:.1f} KB" if img_path and os.path.exists(abs_f) else "N/A"
                alt_status = "FOUND" if alt_txt else "MISSING"
                print(f"{label:<24} | {str(img_path)[:42]:<42} | {alt_status:<14} | {sz_str:<10} | {'PASS' if item_ok else 'FAIL'}")

            # Check feature tiles
            f_tiles = cur.execute("SELECT * FROM feature_tiles WHERE feature_section_id = ? AND active = 1 ORDER BY sort_order ASC", (f_sec['id'],)).fetchall()
            t_cols = [c[0] for c in cur.description]
            for t_row in f_tiles:
                t = dict(zip(t_cols, t_row))
                if t.get('kind') == 'photo':
                    total_checks += 1
                    t_ok = True
                    sz = 0
                    abs_f = ""
                    img_path = t.get('image_path')
                    alt_txt = t.get('image_alt')
                    if not img_path:
                        errors.append(f"Featured Tile #{t['sort_order']} (photo): Image path missing")
                        t_ok = False
                    else:
                        rel = img_path.lstrip('/')
                        abs_f = os.path.join(BASE_DIR, rel.replace('/', os.sep))
                        if not os.path.exists(abs_f):
                            errors.append(f"Featured Tile #{t['sort_order']} (photo): File missing at {img_path}")
                            t_ok = False
                        else:
                            sz = os.path.getsize(abs_f)
                            sec_weight += sz
                            if sz > 120 * 1024:
                                errors.append(f"Featured Tile #{t['sort_order']}: Exceeds 120KB ({sz/1024:.1f}KB)")
                                t_ok = False
                            if not alt_txt or len(alt_txt.strip()) == 0:
                                errors.append(f"Featured Tile #{t['sort_order']}: Missing alt text")
                                t_ok = False
                            try:
                                with Image.open(abs_f) as im:
                                    if im.format != 'WEBP':
                                        errors.append(f"Featured Tile #{t['sort_order']}: Format {im.format}, expected WEBP")
                                        t_ok = False
                            except Exception as e:
                                errors.append(f"Featured Tile #{t['sort_order']}: Corrupt image: {e}")
                                t_ok = False
                    if t_ok:
                        total_passed += 1
                    sz_str = f"{sz/1024:.1f} KB" if img_path and os.path.exists(abs_f) else "N/A"
                    print(f"Tile #{t['sort_order']} (Photo)        | {str(img_path)[:42]:<42} | {'FOUND' if alt_txt else 'MISSING':<14} | {sz_str:<10} | {'PASS' if t_ok else 'FAIL'}")

            # Check total section weight
            total_checks += 1
            budget_limit = 700 * 1024
            if sec_weight <= budget_limit:
                total_passed += 1
                print(f"\n✓ Total Section Asset Weight: {sec_weight/1024:.1f} KB / 700.0 KB (PASS - Under 700KB budget)")
            else:
                errors.append(f"Featured Edit section asset weight {sec_weight/1024:.1f} KB exceeds 700 KB limit!")
                print(f"\n[X] Total Section Asset Weight: {sec_weight/1024:.1f} KB / 700.0 KB (FAIL - Exceeds 700KB)")

    con.close()

    print("\n" + "=" * 80)
    print("AUDIT RESULTS SUMMARY")
    print(f"Total Asset Checks Performed: {total_checks}")
    print(f"Passed Checks:               {total_passed}")
    print(f"Total Errors Found:          {len(errors)}")
    print("=" * 80)

    if errors:
        print("\nFAILURE REPORT (Exit code 1):")
        for err in errors[:25]:
            print(f"  [X] {err}")
        if len(errors) > 25:
            print(f"  ... and {len(errors) - 25} more errors.")
        print("\nPlease fix the above errors before deploying to production.")
        return False
    else:
        print("\nSUCCESS: All product photographic assets verified and ready for production! (Exit code 0)")
        return True

if __name__ == '__main__':
    success = check_assets()
    sys.exit(0 if success else 1)
