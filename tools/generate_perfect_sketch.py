import os
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont

BASE_DIR = r"E:\jewelery"
SOLITAIRE_SRC = os.path.join(BASE_DIR, "scratch_test_ring_solitaire.jpg")
OUT_SKETCH = os.path.join(BASE_DIR, "static", "sketches", "the-empress-cushion-solitaire.webp")

def make_empress_sketch():
    src = Image.open(SOLITAIRE_SRC).convert('RGB')
    w, h = 800, 533
    src = src.resize((w, h), Image.Resampling.LANCZOS)

    # 1. Base cream paper (#efe4cc = 239, 228, 204)
    paper = Image.new('RGB', (w, h), (239, 228, 204))
    draw = ImageDraw.Draw(paper)

    # Drafting millimeter grid
    for x in range(0, w, 25):
        draw.line([(x, 0), (x, h)], fill=(228, 217, 192), width=1)
    for y in range(0, h, 25):
        draw.line([(0, y), (w, y)], fill=(228, 217, 192), width=1)
    for x in range(0, w, 100):
        draw.line([(x, 0), (x, h)], fill=(214, 200, 174), width=1)
    for y in range(0, h, 100):
        draw.line([(0, y), (w, y)], fill=(214, 200, 174), width=1)

    gray = src.convert('L')
    
    # Ring mask (bright pixels on dark background)
    ring_mask = gray.point(lambda p: 255 if p > 55 else 0).filter(ImageFilter.GaussianBlur(1.0))
    
    # Fine facet lines (sobel-like edge detection)
    edges1 = gray.filter(ImageFilter.FIND_EDGES)
    edges2 = gray.filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.FIND_EDGES)
    edges = Image.blend(edges1, edges2, 0.5)
    edges = ImageEnhance.Contrast(edges).enhance(3.5)

    paper_pixels = paper.load()
    edges_pixels = edges.load()
    gray_pixels = gray.load()
    mask_pixels = ring_mask.load()

    # Graphite ink:
    # 2B/4B dark pencil: (22, 26, 36)
    # Mid-tone graphite: (55, 62, 75)
    # Light graphite: (95, 102, 115)

    for y in range(h):
        for x in range(w):
            m = mask_pixels[x, y]
            if m > 15:
                g = gray_pixels[x, y]
                e = edges_pixels[x, y]
                alpha = m / 255.0

                if e > 30:
                    # Dark pencil stroke
                    stroke_w = min(1.0, e / 95.0) * alpha
                    r = int(239 * (1 - stroke_w) + 20 * stroke_w)
                    g = int(228 * (1 - stroke_w) + 24 * stroke_w)
                    b = int(204 * (1 - stroke_w) + 34 * stroke_w)
                    paper_pixels[x, y] = (r, g, b)
                else:
                    # Tonal graphite shading
                    # Contrast curve for metal & diamond shading
                    shade_factor = max(0.0, (230 - g) / 200.0)
                    if shade_factor > 0.15:
                        shade_w = min(0.65, (shade_factor - 0.15) * 1.3) * alpha
                        r = int(239 * (1 - shade_w) + 52 * shade_w)
                        g = int(228 * (1 - shade_w) + 60 * shade_w)
                        b = int(204 * (1 - shade_w) + 72 * shade_w)
                        paper_pixels[x, y] = (r, g, b)

    # Architectural Calipers & Annotations
    cx, cy = 400, 238

    # Halo diameter caliper (positioned cleanly above the ring)
    caliper_y = cy - 110
    draw.line([(cx - 86, caliper_y), (cx + 86, caliper_y)], fill=(55, 48, 40), width=1)
    # Ticks
    draw.line([(cx - 86, caliper_y - 6), (cx - 86, caliper_y + 6)], fill=(55, 48, 40), width=1)
    draw.line([(cx + 86, caliper_y - 6), (cx + 86, caliper_y + 6)], fill=(55, 48, 40), width=1)
    # Projection extension lines
    draw.line([(cx - 86, caliper_y + 6), (cx - 86, cy - 88)], fill=(160, 150, 135), width=1)
    draw.line([(cx + 86, caliper_y + 6), (cx + 86, cy - 88)], fill=(160, 150, 135), width=1)
    draw.text((cx - 30, caliper_y - 18), "8.20 mm", fill=(45, 38, 30))

    # Shank width caliper (positioned to the right)
    caliper_x = 610
    draw.line([(caliper_x, cy - 40), (caliper_x, cy + 40)], fill=(65, 58, 50), width=1)
    draw.line([(caliper_x - 6, cy - 40), (caliper_x + 6, cy - 40)], fill=(65, 58, 50), width=1)
    draw.line([(caliper_x - 6, cy + 40), (caliper_x + 6, cy + 40)], fill=(65, 58, 50), width=1)
    draw.line([(580, cy - 40), (caliper_x - 6, cy - 40)], fill=(160, 150, 135), width=1)
    draw.line([(580, cy + 40), (caliper_x - 6, cy + 40)], fill=(160, 150, 135), width=1)
    draw.text((caliper_x + 12, cy - 7), "~ 1.8mm shank", fill=(55, 48, 40))

    # Archival Bench Margin Notes (Clean ASCII, no missing characters)
    draw.text((40, 32), "ATELIER NILAYA - ARCHIVAL BENCH DRAFT", fill=(45, 38, 30))
    draw.text((40, 52), "PLATE NO. 1987-B - SURAT GUILD", fill=(80, 70, 60))

    draw.text((40, h - 90), "- 2.20ct Cushion Brilliant Solitaire (VVS1)", fill=(40, 35, 28))
    draw.text((40, h - 70), "- Hand-carved 4-prong split-shank gallery", fill=(60, 52, 45))
    draw.text((40, h - 50), "- Solid Pt950 core & 18K rose gold halo bezel", fill=(60, 52, 45))
    draw.text((40, h - 30), "- Surat Atelier Bench #1 - 14/03/1987 - Master N.K.", fill=(80, 70, 60))

    draw.text((w - 160, h - 30), "SCALE 1:1 - 1987", fill=(75, 68, 60))

    paper.save(OUT_SKETCH, 'WEBP', quality=85)
    print(f"Generated {OUT_SKETCH} ({os.path.getsize(OUT_SKETCH) / 1024:.1f} KB)")

if __name__ == '__main__':
    make_empress_sketch()
