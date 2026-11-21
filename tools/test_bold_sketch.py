#!/usr/bin/env python3
"""
Test generator for high-contrast, boldly visible jeweler's graphite pencil sketch.
Produces unmistakable hand-drawn graphite lines, facet cross-hatching, and technical annotations.
"""

import os
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw

BASE_DIR = r"E:\jewelery"
SRC_PATH = os.path.join(BASE_DIR, 'static', 'products', 'the-empress-cushion-solitaire-2-2ct', 'platinum', 'front.webp')
OUT_PATH = os.path.join(BASE_DIR, 'static', 'sketches', 'the-empress-cushion-solitaire.webp')

def generate_bold_sketch():
    src = Image.open(SRC_PATH).convert('RGB')
    w, h = src.size

    # Background color of the source image
    bg_color = src.getpixel((10, 10))

    # 1. Base cream parchment paper (#efe4cc = RGB 239, 228, 204)
    paper = Image.new('RGB', (w, h), (239, 228, 204))
    draw = ImageDraw.Draw(paper)

    # 2. Draw millimeter drafting grid
    for x in range(0, w, 30):
        draw.line([(x, 0), (x, h)], fill=(225, 214, 188), width=1)
    for y in range(0, h, 30):
        draw.line([(0, y), (w, y)], fill=(225, 214, 188), width=1)
    # Major grid every 120px
    for x in range(0, w, 120):
        draw.line([(x, 0), (x, h)], fill=(212, 198, 172), width=1)
    for y in range(0, h, 120):
        draw.line([(0, y), (w, y)], fill=(212, 198, 172), width=1)

    # 3. Create high-contrast line work and graphite shading from the ring
    gray = src.convert('L')

    # Detect the mask of the ring (where pixel differs from background)
    ring_mask = Image.new('L', (w, h), 0)
    for y in range(h):
        for x in range(w):
            p = src.getpixel((x, y))
            diff = max(abs(p[0] - bg_color[0]), abs(p[1] - bg_color[1]), abs(p[2] - bg_color[2]))
            if diff > 18:
                ring_mask.putpixel((x, y), 255)

    # Edge detection: Fine details and contours
    edges1 = gray.filter(ImageFilter.FIND_EDGES)
    edges2 = gray.filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.FIND_EDGES)
    edges = Image.blend(edges1, edges2, 0.5)

    # Boost edge contrast
    enhancer = ImageEnhance.Contrast(edges)
    edges_boosted = enhancer.enhance(3.5)

    # Extract metal shading (invert luminance inside ring mask to represent graphite density)
    # Dark areas in photo (grooves, prongs, shadows) should be dark graphite
    # Bright reflections should be paper or light graphite shading
    shading = ImageOps.invert(gray)

    # Composite pencil art onto cream paper
    paper_pixels = paper.load()
    edges_pixels = edges_boosted.load()
    shading_pixels = shading.load()
    mask_pixels = ring_mask.load()

    # Graphite ink colors
    # Dark 2B/4B line: (28, 32, 42)
    # Medium graphite shade: (65, 72, 85)
    for y in range(h):
        for x in range(w):
            if mask_pixels[x, y] > 0:
                edge_val = edges_pixels[x, y]
                shade_val = shading_pixels[x, y]

                # Strong pencil line for edges
                if edge_val > 35:
                    # Blend towards dark graphite
                    line_weight = min(1.0, edge_val / 120.0)
                    r = int(239 * (1 - line_weight) + 26 * line_weight)
                    g = int(228 * (1 - line_weight) + 30 * line_weight)
                    b = int(204 * (1 - line_weight) + 40 * line_weight)
                    paper_pixels[x, y] = (r, g, b)
                elif shade_val > 50:
                    # Soft graphite tonal shading
                    shade_weight = min(0.65, (shade_val - 50) / 180.0)
                    r = int(239 * (1 - shade_weight) + 60 * shade_weight)
                    g = int(228 * (1 - shade_weight) + 68 * shade_weight)
                    b = int(204 * (1 - shade_weight) + 82 * shade_weight)
                    paper_pixels[x, y] = (r, g, b)

    # 4. Add architectural jeweler's drafting annotations & caliper lines
    # Dimension arrows around the cushion solitaire head
    cx, cy = w // 2, 190
    draw.line([(cx - 95, cy - 80), (cx + 95, cy - 80)], fill=(60, 52, 45), width=1)
    draw.line([(cx - 95, cy - 86), (cx - 95, cy - 74)], fill=(60, 52, 45), width=1)
    draw.line([(cx + 95, cy - 86), (cx + 95, cy - 74)], fill=(60, 52, 45), width=1)
    draw.text((cx - 45, cy - 100), "8.20 mm", fill=(50, 42, 35))

    # Shank caliper line
    draw.line([(w - 110, 310), (w - 110, 460)], fill=(70, 62, 55), width=1)
    draw.line([(w - 116, 310), (w - 104, 310)], fill=(70, 62, 55), width=1)
    draw.line([(w - 116, 460), (w - 104, 460)], fill=(70, 62, 55), width=1)
    draw.text((w - 95, 375), "\u2248 1.8mm shank", fill=(55, 48, 40))

    # Workshop technical notes in margins
    draw.text((36, 28), "ATELIER NILAYA \u2022 ARCHIVAL BENCH DRAFT", fill=(50, 42, 35))
    draw.text((36, 46), "PLATE NO. 1987-B \u2022 SURAT GUILD", fill=(80, 70, 60))

    draw.text((36, h - 85), "\u2014 2.20ct Cushion Brilliant Solitaire (VVS1)", fill=(40, 35, 30))
    draw.text((36, h - 68), "\u2014 Hand-carved 4-prong split-shank gallery", fill=(60, 52, 45))
    draw.text((36, h - 51), "\u2014 Solid Pt950 core & 18K yellow under-bezel", fill=(60, 52, 45))
    draw.text((36, h - 34), "\u2014 Surat Atelier Bench #1 \u2022 14/03/1987 \u2022 Master N.K.", fill=(80, 70, 60))

    draw.text((w - 150, h - 34), "SCALE 1:1 \u2022 1987", fill=(75, 68, 60))

    # Save as high-quality WebP
    paper.save(OUT_PATH, 'WEBP', quality=90)
    print(f"Generated bold sketch: {OUT_PATH} ({os.path.getsize(OUT_PATH) / 1024:.1f} KB)")

if __name__ == '__main__':
    generate_bold_sketch()
