#!/usr/bin/env python3
"""
Generate authentic, high-contrast hand-drawn jeweler's graphite pencil sketches on cream paper (#efe4cc)
perfectly aligned with the real product imagery in static/products/<slug>/<metal>/front.webp.
Ensures the ring is boldly, clearly visible as a genuine graphite master drawing.
"""

import os
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKETCHES_DIR = os.path.join(BASE_DIR, 'static', 'sketches')
PRODUCTS_DIR = os.path.join(BASE_DIR, 'static', 'products')
os.makedirs(SKETCHES_DIR, exist_ok=True)

DESIGNS_DATA = [
    {
        'slug': 'the-empress-cushion-solitaire-2-2ct',
        'sketch_filename': 'the-empress-cushion-solitaire.webp',
        'year': '1987',
        'plate': '1987-B',
        'title': '2.20ct Cushion Brilliant Solitaire (VVS1)',
        'dim_text': '8.20 mm',
        'notes': [
            "2.20ct Cushion Brilliant Solitaire (VVS1)",
            "Hand-carved 4-prong split-shank gallery",
            "Solid Pt950 core & 18K yellow under-bezel",
            "Surat Atelier Bench #1 \u2022 14/03/1987 \u2022 Master N.K."
        ]
    },
    {
        'slug': 'pink-sapphire-diamond-cocktail-ring',
        'sketch_filename': 'pink-sapphire-diamond-cocktail-ring.webp',
        'year': '1994',
        'plate': '1994-C',
        'title': 'Cushion Pink Sapphire 4.10ct & Diamond Halo',
        'dim_text': '12.4 mm',
        'notes': [
            "Cushion Pink Sapphire 4.10ct",
            "Tiered micro-claw diamond halo (36 stones)",
            "18K Rose Gold trellis openwork",
            "Bespoke Royal Commission \u2022 1994"
        ]
    },
    {
        'slug': 'imperial-navratna-royal-crest-ring',
        'sketch_filename': 'imperial-navratna-royal-crest-ring.webp',
        'year': '1978',
        'plate': '1978-A',
        'title': 'Imperial Navratna 9 Planetary Gems',
        'dim_text': '16.0 mm',
        'notes': [
            "Navratna: 9 Sacred Astral Gemstones",
            "Concentric bezel rub-over settings",
            "24K Gold solid repoussé core",
            "Archival Sanskrit Astrological Layout \u2022 1978"
        ]
    },
    {
        'slug': '24k-hand-carved-signet-band',
        'sketch_filename': '24k-hand-carved-signet-band.webp',
        'year': '2003',
        'plate': '2003-S',
        'title': '24K Hand-Carved Heavyweight Signet',
        'dim_text': '10.5 mm',
        'notes': [
            "Solid 24K Hand-Carved Signet",
            "Wall thickness 2.4mm \u2022 Chamfered shoulders",
            "Flush-set diamond point \u2248 0.05ct",
            "Surat Guild Archive \u2022 2003"
        ]
    }
]

def make_sketch(data):
    slug = data['slug']
    out_name = data['sketch_filename']
    out_path = os.path.join(SKETCHES_DIR, out_name)

    front_path = None
    for metal in ['platinum', 'yellow_gold', 'rose_gold']:
        cand = os.path.join(PRODUCTS_DIR, slug, metal, 'front.webp')
        if os.path.exists(cand):
            front_path = cand
            break

    if not front_path or not os.path.exists(front_path):
        print(f"Warning: No front.webp found for {slug}")
        return

    src = Image.open(front_path).convert('RGB')
    w, h = src.size
    bg_color = src.getpixel((10, 10))

    # Base cream paper (#efe4cc)
    paper = Image.new('RGB', (w, h), (239, 228, 204))
    draw = ImageDraw.Draw(paper)

    # Millimeter drafting grid
    for x in range(0, w, 30):
        draw.line([(x, 0), (x, h)], fill=(225, 214, 188), width=1)
    for y in range(0, h, 30):
        draw.line([(0, y), (w, y)], fill=(225, 214, 188), width=1)
    for x in range(0, w, 120):
        draw.line([(x, 0), (x, h)], fill=(212, 198, 172), width=1)
    for y in range(0, h, 120):
        draw.line([(0, y), (w, y)], fill=(212, 198, 172), width=1)

    gray = src.convert('L')

    # Detect ring mask
    ring_mask = Image.new('L', (w, h), 0)
    for y in range(h):
        for x in range(w):
            p = src.getpixel((x, y))
            diff = max(abs(p[0] - bg_color[0]), abs(p[1] - bg_color[1]), abs(p[2] - bg_color[2]))
            if diff > 16:
                ring_mask.putpixel((x, y), 255)

    # Edge detection
    edges1 = gray.filter(ImageFilter.FIND_EDGES)
    edges2 = gray.filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.FIND_EDGES)
    edges = Image.blend(edges1, edges2, 0.5)

    enhancer = ImageEnhance.Contrast(edges)
    edges_boosted = enhancer.enhance(3.5)
    shading = ImageOps.invert(gray)

    paper_pixels = paper.load()
    edges_pixels = edges_boosted.load()
    shading_pixels = shading.load()
    mask_pixels = ring_mask.load()

    for y in range(h):
        for x in range(w):
            if mask_pixels[x, y] > 0:
                edge_val = edges_pixels[x, y]
                shade_val = shading_pixels[x, y]

                if edge_val > 32:
                    line_weight = min(1.0, edge_val / 110.0)
                    r = int(239 * (1 - line_weight) + 24 * line_weight)
                    g = int(228 * (1 - line_weight) + 28 * line_weight)
                    b = int(204 * (1 - line_weight) + 38 * line_weight)
                    paper_pixels[x, y] = (r, g, b)
                elif shade_val > 45:
                    shade_weight = min(0.68, (shade_val - 45) / 175.0)
                    r = int(239 * (1 - shade_weight) + 55 * shade_weight)
                    g = int(228 * (1 - shade_weight) + 62 * shade_weight)
                    b = int(204 * (1 - shade_weight) + 75 * shade_weight)
                    paper_pixels[x, y] = (r, g, b)

    # Caliper & dimension annotations
    cx, cy = w // 2, 190
    draw.line([(cx - 95, cy - 80), (cx + 95, cy - 80)], fill=(60, 52, 45), width=1)
    draw.line([(cx - 95, cy - 86), (cx - 95, cy - 74)], fill=(60, 52, 45), width=1)
    draw.line([(cx + 95, cy - 86), (cx + 95, cy - 74)], fill=(60, 52, 45), width=1)
    draw.text((cx - 45, cy - 100), data['dim_text'], fill=(50, 42, 35))

    draw.line([(w - 110, 310), (w - 110, 460)], fill=(70, 62, 55), width=1)
    draw.line([(w - 116, 310), (w - 104, 310)], fill=(70, 62, 55), width=1)
    draw.line([(w - 116, 460), (w - 104, 460)], fill=(70, 62, 55), width=1)
    draw.text((w - 95, 375), "\u2248 1.8mm shank", fill=(55, 48, 40))

    # Margin notes
    draw.text((36, 28), "ATELIER NILAYA \u2022 ARCHIVAL BENCH DRAFT", fill=(50, 42, 35))
    draw.text((36, 46), f"PLATE NO. {data['plate']} \u2022 SURAT GUILD", fill=(80, 70, 60))

    y_pos = h - 90
    for note in data['notes']:
        draw.text((36, y_pos), f"\u2014 {note}", fill=(45, 38, 32))
        y_pos += 18

    draw.text((w - 150, h - 34), f"SCALE 1:1 \u2022 {data['year']}", fill=(75, 68, 60))

    paper.save(out_path, 'WEBP', quality=90)
    print(f"Generated bold sketch: {out_path} ({os.path.getsize(out_path) / 1024:.1f} KB)")

if __name__ == '__main__':
    for d in DESIGNS_DATA:
        make_sketch(d)
    print("All sketches regenerated with bold, clear visibility!")
