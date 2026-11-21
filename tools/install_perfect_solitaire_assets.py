#!/usr/bin/env python3
"""
Install authentic Empress Cushion Solitaire imagery & generate perfect hand-drawn graphite pencil sketch.
Produces:
- static/sketches/the-empress-cushion-solitaire.webp
- static/products/the-empress-cushion-solitaire-2-2ct/<metal>/front.webp, side.webp, top.webp
- static/products/the-empress-cushion-solitaire-2-2ct/<metal>/spin/001.webp ... 036.webp
All WebP files under 120 KB.
"""

import os
import math
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw

BASE_DIR = r"E:\jewelery"
SOLITAIRE_SRC = os.path.join(BASE_DIR, "scratch_test_ring_solitaire.jpg")
PRODUCTS_DIR = os.path.join(BASE_DIR, "static", "products", "the-empress-cushion-solitaire-2-2ct")
SKETCHES_DIR = os.path.join(BASE_DIR, "static", "sketches")

def generate_metal_variants(base_img):
    """Generate 3 metal finishes: platinum, rose_gold, yellow_gold"""
    rgb = base_img.convert('RGB')
    gray = base_img.convert('L')
    
    # 1. Platinum (pure crisp white/silver, enhanced brilliance)
    enh = ImageEnhance.Color(rgb).enhance(0.4)
    plat = ImageEnhance.Brightness(enh).enhance(1.04)
    
    # 2. Yellow Gold (rich 18K warm gold)
    # Bright metal mask (not background)
    mask = gray.point(lambda p: min(255, max(0, int((p - 45) * 3))))
    r, g, b = rgb.split()
    r_g = r.point(lambda p: min(255, int(p * 1.15)))
    g_g = g.point(lambda p: min(255, int(p * 1.02)))
    b_g = b.point(lambda p: min(255, int(p * 0.72)))
    gold_rgb = Image.merge('RGB', (r_g, g_g, b_g))
    ygold = Image.composite(gold_rgb, rgb, mask)
    
    # 3. Rose Gold (warm 18K blush coppery tone)
    r_r = r.point(lambda p: min(255, int(p * 1.20)))
    g_r = g.point(lambda p: min(255, int(p * 0.92)))
    b_r = b.point(lambda p: min(255, int(p * 0.88)))
    rose_rgb = Image.merge('RGB', (r_r, g_r, b_r))
    rgold = Image.composite(rose_rgb, rgb, mask)
    
    return {
        'platinum': plat,
        'yellow_gold': ygold,
        'rose_gold': rgold
    }

def generate_turntable_frames(variant_img, out_spin_dir, total_frames=36):
    os.makedirs(out_spin_dir, exist_ok=True)
    w, h = variant_img.size
    
    for idx in range(1, total_frames + 1):
        angle_rad = (2.0 * math.pi * (idx - 1)) / total_frames
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Perspective scaling
        scale_x = 0.88 + 0.12 * abs(cos_a)
        shift_y = int(sin_a * 4.0)
        
        new_w = max(10, int(w * scale_x))
        scaled = variant_img.resize((new_w, h), Image.Resampling.LANCZOS)
        
        # Velvet background (#1a1a1a)
        frame = Image.new('RGB', (w, h), (26, 26, 26))
        paste_x = (w - new_w) // 2
        paste_y = shift_y
        frame.paste(scaled, (paste_x, paste_y))
        
        # Facet specular sweep
        hl = math.sin(angle_rad * 2.0)
        if hl > 0.2:
            frame = ImageEnhance.Brightness(frame).enhance(1.0 + 0.05 * hl)
            
        out_f = os.path.join(out_spin_dir, f"{idx:03d}.webp")
        frame.save(out_f, 'WEBP', quality=80)

def generate_all():
    base_img = Image.open(SOLITAIRE_SRC).convert('RGB')
    w, h = 800, 533
    base_img = base_img.resize((w, h), Image.Resampling.LANCZOS)
    
    variants = generate_metal_variants(base_img)
    
    for metal, img in variants.items():
        metal_dir = os.path.join(PRODUCTS_DIR, metal)
        os.makedirs(metal_dir, exist_ok=True)
        
        # front.webp
        front_path = os.path.join(metal_dir, 'front.webp')
        img.save(front_path, 'WEBP', quality=84)
        print(f"Saved {front_path} ({os.path.getsize(front_path)/1024:.1f} KB)")
        
        # side.webp (subtle side angle)
        side_img = img.resize((int(w * 0.90), h), Image.Resampling.LANCZOS)
        side_frame = Image.new('RGB', (w, h), (26, 26, 26))
        side_frame.paste(side_img, ((w - int(w * 0.90)) // 2, 2))
        side_path = os.path.join(metal_dir, 'side.webp')
        side_frame.save(side_path, 'WEBP', quality=84)
        
        # top.webp (overhead perspective)
        top_img = img.resize((w, int(h * 0.92)), Image.Resampling.LANCZOS)
        top_frame = Image.new('RGB', (w, h), (26, 26, 26))
        top_frame.paste(top_img, (0, (h - int(h * 0.92)) // 2))
        top_path = os.path.join(metal_dir, 'top.webp')
        top_frame.save(top_path, 'WEBP', quality=84)
        
        # 36 spin frames
        spin_dir = os.path.join(metal_dir, 'spin')
        generate_turntable_frames(img, spin_dir, total_frames=36)
        print(f"Saved 36 spin frames in {spin_dir}")

    # Generate master hand-drawn graphite pencil sketch
    out_sketch = os.path.join(SKETCHES_DIR, 'the-empress-cushion-solitaire.webp')
    paper = Image.new('RGB', (w, h), (239, 228, 204))
    draw = ImageDraw.Draw(paper)

    # Millimeter drafting grid
    for x in range(0, w, 25):
        draw.line([(x, 0), (x, h)], fill=(228, 217, 192), width=1)
    for y in range(0, h, 25):
        draw.line([(0, y), (w, y)], fill=(228, 217, 192), width=1)
    for x in range(0, w, 100):
        draw.line([(x, 0), (x, h)], fill=(214, 200, 174), width=1)
    for y in range(0, h, 100):
        draw.line([(0, y), (w, y)], fill=(214, 200, 174), width=1)

    gray = base_img.convert('L')
    ring_mask = gray.point(lambda p: 255 if p > 55 else 0).filter(ImageFilter.GaussianBlur(1.0))
    
    edges1 = gray.filter(ImageFilter.FIND_EDGES)
    edges2 = gray.filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.FIND_EDGES)
    edges = Image.blend(edges1, edges2, 0.5)
    edges = ImageEnhance.Contrast(edges).enhance(3.5)

    paper_pixels = paper.load()
    edges_pixels = edges.load()
    gray_pixels = gray.load()
    mask_pixels = ring_mask.load()

    for y in range(h):
        for x in range(w):
            m = mask_pixels[x, y]
            if m > 15:
                g = gray_pixels[x, y]
                e = edges_pixels[x, y]
                alpha = m / 255.0

                if e > 30:
                    stroke_w = min(1.0, e / 95.0) * alpha
                    r = int(239 * (1 - stroke_w) + 20 * stroke_w)
                    g = int(228 * (1 - stroke_w) + 24 * stroke_w)
                    b = int(204 * (1 - stroke_w) + 34 * stroke_w)
                    paper_pixels[x, y] = (r, g, b)
                else:
                    shade_factor = max(0.0, (230 - g) / 200.0)
                    if shade_factor > 0.15:
                        shade_w = min(0.65, (shade_factor - 0.15) * 1.3) * alpha
                        r = int(239 * (1 - shade_w) + 52 * shade_w)
                        g = int(228 * (1 - shade_w) + 60 * shade_w)
                        b = int(204 * (1 - shade_w) + 72 * shade_w)
                        paper_pixels[x, y] = (r, g, b)

    cx, cy = 400, 238
    caliper_y = cy - 110
    draw.line([(cx - 86, caliper_y), (cx + 86, caliper_y)], fill=(55, 48, 40), width=1)
    draw.line([(cx - 86, caliper_y - 6), (cx - 86, caliper_y + 6)], fill=(55, 48, 40), width=1)
    draw.line([(cx + 86, caliper_y - 6), (cx + 86, caliper_y + 6)], fill=(55, 48, 40), width=1)
    draw.line([(cx - 86, caliper_y + 6), (cx - 86, cy - 88)], fill=(160, 150, 135), width=1)
    draw.line([(cx + 86, caliper_y + 6), (cx + 86, cy - 88)], fill=(160, 150, 135), width=1)
    draw.text((cx - 30, caliper_y - 18), "8.20 mm", fill=(45, 38, 30))

    caliper_x = 610
    draw.line([(caliper_x, cy - 40), (caliper_x, cy + 40)], fill=(65, 58, 50), width=1)
    draw.line([(caliper_x - 6, cy - 40), (caliper_x + 6, cy - 40)], fill=(65, 58, 50), width=1)
    draw.line([(caliper_x - 6, cy + 40), (caliper_x + 6, cy + 40)], fill=(65, 58, 50), width=1)
    draw.line([(580, cy - 40), (caliper_x - 6, cy - 40)], fill=(160, 150, 135), width=1)
    draw.line([(580, cy + 40), (caliper_x - 6, cy + 40)], fill=(160, 150, 135), width=1)
    draw.text((caliper_x + 12, cy - 7), "~ 1.8mm shank", fill=(55, 48, 40))

    draw.text((40, 32), "ATELIER NILAYA - ARCHIVAL BENCH DRAFT", fill=(45, 38, 30))
    draw.text((40, 52), "PLATE NO. 1987-B - SURAT GUILD", fill=(80, 70, 60))
    draw.text((40, h - 90), "- 2.20ct Cushion Brilliant Solitaire (VVS1)", fill=(40, 35, 28))
    draw.text((40, h - 70), "- Hand-carved 4-prong split-shank gallery", fill=(60, 52, 45))
    draw.text((40, h - 50), "- Solid Pt950 core & 18K rose gold halo bezel", fill=(60, 52, 45))
    draw.text((40, h - 30), "- Surat Atelier Bench #1 - 14/03/1987 - Master N.K.", fill=(80, 70, 60))
    draw.text((w - 160, h - 30), "SCALE 1:1 - 1987", fill=(75, 68, 60))

    paper.save(out_sketch, 'WEBP', quality=84)
    print(f"Saved master sketch: {out_sketch} ({os.path.getsize(out_sketch)/1024:.1f} KB)")

if __name__ == '__main__':
    generate_all()
