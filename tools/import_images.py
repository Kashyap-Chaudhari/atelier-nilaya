#!/usr/bin/env python3
"""
Atelier Nilaya — Image Ingestion Tool (import_images.py)
Automates ingestion of studio photography:
1. Scans raw photos named like `<slug>__<metal>__<index>.jpg`
   (e.g. `aarohi-solitaire__yellow-gold__012.jpg`, or `...__front.jpg`, `...__side.jpg`, `...__top.jpg`, `...__lifestyle.jpg`).
2. Auto-crops image to a balanced square on studio backdrop #f6f6f6.
3. Resizes to 1200px (retina @2x) and 600px standard WebP at quality 82.
4. Writes files to exact folder structure:
   static/products/<slug>/<metal>/spin/001.webp ... 036.webp
   static/products/<slug>/<metal>/front.webp, side.webp, top.webp
   static/products/<slug>/lifestyle-1.webp
5. Inserts/updates metadata rows in `product_images` table in `nilaya.db` with generated alt text.

Usage:
  python tools/import_images.py --input-dir /path/to/raw_photos
  python tools/import_images.py --input-file raw/the-empress__platinum__001.jpg
"""

import os
import sys
import re
import argparse
import sqlite3
from PIL import Image, ImageOps

DEFAULT_QUALITY = 82
STUDIO_BG_COLOR = (246, 246, 246)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_PRODUCTS_DIR = os.path.join(BASE_DIR, 'static', 'products')
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'nilaya.db')

def auto_crop_to_square(img, target_bg=STUDIO_BG_COLOR):
    """
    Squares an image centered on the jewellery subject without clipping.
    """
    img = img.convert('RGB')
    w, h = img.size
    
    if w == h:
        return img
        
    size = max(w, h)
    square_canvas = Image.new('RGB', (size, size), target_bg)
    paste_x = (size - w) // 2
    paste_y = (size - h) // 2
    square_canvas.paste(img, (paste_x, paste_y))
    return square_canvas

def parse_filename(filename):
    """
    Parses filename pattern: <slug>__<metal>__<descriptor>.<ext>
    Descriptor can be 001..036, front, side, top, or lifestyle.
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    parts = base.split('__')
    
    if len(parts) >= 3:
        slug = parts[0].strip().lower()
        metal = parts[1].strip().lower().replace('-', '_')
        desc = parts[2].strip().lower()
        return slug, metal, desc
    elif len(parts) == 2:
        slug = parts[0].strip().lower()
        desc = parts[1].strip().lower()
        metal = 'yellow_gold' if desc != 'lifestyle' else 'all'
        return slug, metal, desc
    else:
        return None, None, None

def get_product_info(con, slug):
    cur = con.cursor()
    row = cur.execute("SELECT id, name FROM products WHERE slug = ?", (slug,)).fetchone()
    if row:
        return row[0], row[1]
    return None, None

def process_single_image(file_path, output_dir, con, dry_run=False):
    slug, metal, desc = parse_filename(file_path)
    if not slug or not desc:
        print(f"  [SKIP] Unrecognized filename convention: {os.path.basename(file_path)}")
        return False
        
    p_id, p_name = get_product_info(con, slug)
    if not p_id:
        print(f"  [WARN] Product slug '{slug}' not found in database. Still writing files.")
        p_name = slug.replace('-', ' ').title()

    prod_dir = os.path.join(output_dir, slug)
    os.makedirs(prod_dir, exist_ok=True)
    
    img = Image.open(file_path)
    square_img = auto_crop_to_square(img)
    
    # 600px standard and 1200px retina
    img_600 = square_img.resize((600, 600), Image.Resampling.LANCZOS)
    img_1200 = square_img.resize((1200, 1200), Image.Resampling.LANCZOS)
    
    metal_name_human = metal.replace('_', ' ')

    if desc == 'lifestyle' or desc.startswith('lifestyle'):
        target_path = os.path.join(prod_dir, 'lifestyle-1.webp')
        target_1200 = os.path.join(prod_dir, 'lifestyle-1@2x.webp')
        alt_text = f"{p_name} luxury jewellery lifestyle presentation"
        rel_path = f"/static/products/{slug}/lifestyle-1.webp"
        
        if not dry_run:
            img_600.save(target_path, 'WEBP', quality=DEFAULT_QUALITY)
            img_1200.save(target_1200, 'WEBP', quality=DEFAULT_QUALITY)
            if p_id:
                cur = con.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO product_images (product_id, metal, kind, frame_index, path, alt)
                    VALUES (?, 'all', 'lifestyle', NULL, ?, ?)
                """, (p_id, rel_path, alt_text))
                con.commit()
        print(f"  [SAVED] Lifestyle -> {rel_path}")
        return True

    metal_dir = os.path.join(prod_dir, metal)
    os.makedirs(metal_dir, exist_ok=True)

    if desc in ['front', 'side', 'top']:
        target_path = os.path.join(metal_dir, f"{desc}.webp")
        target_1200 = os.path.join(metal_dir, f"{desc}@2x.webp")
        alt_text = f"{p_name} in {metal_name_human}, {desc} view"
        rel_path = f"/static/products/{slug}/{metal}/{desc}.webp"
        
        if not dry_run:
            img_600.save(target_path, 'WEBP', quality=DEFAULT_QUALITY)
            img_1200.save(target_1200, 'WEBP', quality=DEFAULT_QUALITY)
            if p_id:
                cur = con.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO product_images (product_id, metal, kind, frame_index, path, alt)
                    VALUES (?, ?, ?, NULL, ?, ?)
                """, (p_id, metal, desc, rel_path, alt_text))
                con.commit()
        print(f"  [SAVED] Still {desc} -> {rel_path}")
        return True

    # Check if desc is a spin frame number (e.g. 001, 1, 012)
    m = re.match(r'^(\d+)$', desc)
    if m:
        frame_idx = int(m.group(1))
        spin_dir = os.path.join(metal_dir, 'spin')
        os.makedirs(spin_dir, exist_ok=True)
        
        filename = f"{frame_idx:03d}.webp"
        target_path = os.path.join(spin_dir, filename)
        target_1200 = os.path.join(spin_dir, f"{frame_idx:03d}@2x.webp")
        alt_text = f"{p_name} in {metal_name_human}, 360 view {frame_idx} of 36"
        rel_path = f"/static/products/{slug}/{metal}/spin/{filename}"
        
        if not dry_run:
            img_600.save(target_path, 'WEBP', quality=DEFAULT_QUALITY)
            img_1200.save(target_1200, 'WEBP', quality=DEFAULT_QUALITY)
            if p_id:
                cur = con.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO product_images (product_id, metal, kind, frame_index, path, alt)
                    VALUES (?, ?, 'spin', ?, ?, ?)
                """, (p_id, metal, frame_idx, rel_path, alt_text))
                con.commit()
        print(f"  [SAVED] Spin frame {frame_idx:03d} -> {rel_path}")
        return True

    print(f"  [SKIP] Unhandled descriptor '{desc}' in {os.path.basename(file_path)}")
    return False

def main():
    parser = argparse.ArgumentParser(description="Atelier Nilaya Photo Ingestion Pipeline")
    parser.add_argument('--input-dir', '-d', help="Directory containing raw photos")
    parser.add_argument('--input-file', '-f', help="Single raw photo to process")
    parser.add_argument('--output-dir', '-o', default=STATIC_PRODUCTS_DIR, help="Destination directory (default static/products)")
    parser.add_argument('--db-path', default=DEFAULT_DB_PATH, help="Path to nilaya.db")
    parser.add_argument('--dry-run', action='store_true', help="Preview actions without writing files or database rows")
    args = parser.parse_args()

    if not args.input_dir and not args.input_file:
        parser.print_help()
        sys.exit(1)

    con = sqlite3.connect(args.db_path)
    
    if args.input_file:
        print(f"Processing single file: {args.input_file}")
        process_single_image(args.input_file, args.output_dir, con, args.dry_run)
    elif args.input_dir:
        print(f"Scanning directory: {args.input_dir}")
        count = 0
        for root, dirs, files in os.walk(args.input_dir):
            for file in sorted(files):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    full_path = os.path.join(root, file)
                    if process_single_image(full_path, args.output_dir, con, args.dry_run):
                        count += 1
        print(f"\nCompleted! Processed {count} images.")
        
    con.close()

if __name__ == '__main__':
    main()
