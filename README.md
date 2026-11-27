# Atelier Nilaya — High Jewellery Photographic Image System & 360° Turntable Engine

Atelier Nilaya (Surat, Gujarat • Est. 1954).
This project replaces procedurally generated 3D geometry with an authentic, studio-grade photographic 360-degree turntable image system and multi-angle still photography gallery.

---

## 1. System Architecture & Folder Layout

Every jewellery artwork has, per offered metal variant (`yellow_gold`, `rose_gold`, `platinum`, `silver`), an interactive 36-frame 360° turntable spin sequence, 3 still angles (`front`, `side`, `top`), and an on-hand or on-neck lifestyle presentation:

```
static/products/<slug>/
├── <metal>/
│   ├── spin/
│   │   ├── 001.webp       (0° front turntable view)
│   │   ├── 002.webp       (10° step)
│   │   ├── ...
│   │   └── 036.webp       (350° step)
│   ├── front.webp         (Primary hero still angle)
│   ├── side.webp          (Architectural profile still)
│   └── top.webp           (Top-down elevation perspective)
└── lifestyle-1.webp       (High-resolution worn editorial on hand/neck)
```

### Visual Specifications
- **Format**: WebP (quality 82, under 45 KB per frame; strict limit < 120 KB).
- **Backdrop**: Studio `#f6f6f6` seamless clean background matching product tiles.
- **Dimensions**: Uniform 600×600 px standard, 1200×1200 px retina @2x.
- **Performance**: Preloads only frame `001.webp` on load; frames `002`–`036` are lazy-loaded via `IntersectionObserver` (`rootMargin: 200px`). Total page weight before scrolling is under 1.5 MB.

---

## 2. Studio Jewellery Photography Guide

To photograph a jewellery piece for the 360° turntable system:

1. **Light Tent & Sweep**:
   - Use a small light tent or a seamless white-to-light-grey sweep (`#f6f6f6`).
2. **Lighting Geometry**:
   - Set two diffused softbox lights at 45-degree angles to the piece to illuminate metal facets while preventing harsh specular burn.
   - Use a top overhead fill light for gemstone dispersion and facet sparkle.
3. **Turntable**:
   - Use a precision manual or motorised turntable calibrated to 10-degree increments (yielding exactly 36 shots per 360° revolution).
4. **Camera & Tripod**:
   - Mount a professional camera with a macro lens (85mm–105mm) on a rigid tripod.
   - Position camera at a 15°–20° elevation angle looking down into the setting.
5. **Exposure & White Balance Lock**:
   - Lock manual exposure, aperture (f/11 to f/16 for deep depth of field), ISO (100), and custom white balance (5500K). Never use auto-exposure or auto-white balance between frames.
6. **Centring & Preparation**:
   - Carefully centre the piece on the turntable rotation axis so it does not wobble as it turns.
   - Clean the piece with an ultrasonic bath and lint-free jewellery cloth prior to shooting.
7. **Metal Variants**:
   - Photograph each metal alloy variant (`yellow_gold`, `rose_gold`, `platinum`, `silver`) as its own dedicated 36-frame sequence.

---

## 3. Raw File Naming Conventions

Save raw camera exposures using the double-underscore convention:
```
<slug>__<metal>__<index_or_kind>.jpg
```

### Examples:
- 360° Spin frame 12: `aarohi-solitaire__yellow-gold__012.jpg`
- Hero Front angle: `aarohi-solitaire__yellow-gold__front.jpg`
- Side Profile: `aarohi-solitaire__yellow-gold__side.jpg`
- Top View: `aarohi-solitaire__yellow-gold__top.jpg`
- Lifestyle photograph: `aarohi-solitaire__lifestyle.jpg`

---

## 4. Python Build Tools (`/tools`)

### Tool 1: `tools/import_images.py`
Auto-crops raw studio photos to a centered square, resizes to 1200 px and 600 px WebP (quality 82), places them into the folder hierarchy, and writes metadata into `product_images`:

```bash
# Ingest an entire folder of raw photos:
python tools/import_images.py --input-dir /path/to/raw_photos

# Ingest a single raw frame:
python tools/import_images.py --input-file raw/the-empress__platinum__001.jpg
```

### Tool 2: `tools/render_turntable.py`
Blender (`bpy`) script to render a 36-frame turntable sequence from a 3D CAD `.glb` model using calibrated PBR metal presets:

```bash
# Exact Blender CLI command:
blender -b -P tools/render_turntable.py -- --input path/to/model.glb --slug the-empress-cushion-solitaire-2-2ct --metal yellow_gold
```

### Tool 3: `tools/check_assets.py`
Quality assurance auditor. For every product and offered metal (`in_stock = 1` in `product_metals`), verifies:
- All 36 spin frames exist (`001.webp` to `036.webp`).
- All 3 still angles exist (`front.webp`, `side.webp`, `top.webp`).
- Lifestyle photo exists (`lifestyle-1.webp`).
- All files are valid WebP, square, and strictly under 120 KB each.
- Returns exit code `0` on success, or exit code `1` with a detailed error report.

```bash
# Run asset audit:
python tools/check_assets.py
```

---

## 5. How to Add a New Product

1. **Insert into Database**:
   ```sql
   INSERT INTO products (category_id, name, slug, price, base_metal, purity, approx_weight, stone, certificate, description, spin_frames)
   VALUES (1, 'Aarohi Solitaire Ring', 'aarohi-solitaire-ring', 245000.0, 'yellow_gold', '22K Gold', '6.8 g', '1.5ct Solitaire Diamond', 'GIA Certified', 'Handcrafted solitaire ring.', 36);
   
   INSERT INTO product_metals (product_id, metal, price, in_stock) VALUES
   (LAST_INSERT_ROWID(), 'yellow_gold', 245000.0, 1),
   (LAST_INSERT_ROWID(), 'rose_gold', 255000.0, 1),
   (LAST_INSERT_ROWID(), 'platinum', 285000.0, 1);
   ```
2. **Process Photography**:
   Place raw photos into a folder and run:
   ```bash
   python tools/import_images.py --input-dir /path/to/new_photos
   ```
3. **Verify Quality**:
   ```bash
   python tools/check_assets.py
   ```

---

## 6. Verification & Test Checklist

- [x] **Drag Rotation**: Dragging left or right scrubs through the 36 turntable frames with realistic inertia on release.
- [x] **Touch Swipes**: Vertical touch swipes scroll the webpage smoothly without getting trapped; horizontal swipes scrub frames.
- [x] **Keyboard Accessibility**: Tabbing onto the stage and pressing `ArrowLeft` or `ArrowRight` steps exactly 1 frame.
- [x] **Metal Swatches**: Clicking a metal dot switches to that metal's frames, updates displayed price and "Save N%" discount badge, and updates the URL parameter `metal_dot`.
- [x] **Offered Metals Only**: Dots are only displayed for metals offered for that specific piece.
- [x] **Hover Second View**: Hovering over a tile on desktop reveals `lifestyle-1.webp` (worn on hand or neck).
- [x] **Fallback Order**: Missing spin falls back to `front.webp`, then to the neutral "Photo coming soon" tile in the same aspect ratio.
- [x] **Asset Auditor**: `python tools/check_assets.py` passes with 2044/2044 checks (exit code 0); flags errors on missing files (exit code 1).
- [x] **Mobile Responsiveness**: Clean 2-column layout at 360 px width with zero layout shift.

---

## 7. Featured Edit Section (Faded Photo Band + 12-Column Editorial Grid)

The **Featured Edit** is an editorial mid-page showcase placed between the Craftsmanship ("How a piece is made") section and strictly before the permanent catalogue ("Four Master Chapters of The Atelier"). It combines two complementary references:
1. **Reference A (Top)**: A faded photo band with a lifestyle photo melting into `#25101f` plum via pure CSS `mask-image`, left-aligned typography meeting WCAG AA contrast (13.5:1), and 3 desktop hexagon frames with 14px offset champagne outlines.
2. **Reference B (Bottom)**: A 12-column editorial grid (6px gaps, zero card borders) blending full-bleed photography, real database products on `#f6f6f6`, and flat taupe (`#7d6b57`) / cream (`#efeae4`) text blocks with spaced serif capitals.

### Photo Requirements
- **Band Photo (`bg_image_path`)**: Landscape, at least 1920×1000 px. The jewellery model/subject must sit in the right two-thirds of the frame, with a calm, darker negative-space area on the left for readable typography. **Do not bake any fade or vignette into the image**; all edge blending, transparency gradients, and plum tinting are rendered live in CSS via `-webkit-mask-image` and `rgba(37, 16, 31, 0.55)`.
- **Hexagon Photos (`hex_1_path`, `hex_2_path`, `hex_3_path`)**: Square, at least 1000×1000 px, with the jewellery piece and model's hands/neck framed in the dead centre. Clipped to `polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)`.
- **Editorial Tile Photos (`image_path`)**: Consistent colour grading and warmth across all pictures, under 120 KB each in WebP format.
- **Product Tiles**: Isolated high-jewellery photography on uniform light grey `#f6f6f6` backgrounds, square aspect ratio.

### How to Add or Reorder Tiles
Tiles are stored in SQLite in the `feature_tiles` table and ordered dynamically by `sort_order ASC`:
- **Add a new lifestyle photo**:
  ```sql
  INSERT INTO feature_tiles (feature_section_id, sort_order, kind, title, link, image_path, image_alt, active)
  VALUES (1, 8, 'photo', 'Heritage Chandelier Suite', '/c/earrings', '/static/lifestyle/lifestyle-product-5.webp', 'Model wearing emerald chandelier earrings', 1);
  ```
- **Reorder existing tiles**:
  ```sql
  UPDATE feature_tiles SET sort_order = 1 WHERE id = 3; -- Put manifesto first
  ```
- **Change a text block's copy or button**:
  ```sql
  UPDATE feature_tiles SET title = 'THE LAPIDARY BENCHES', body = 'Over seven decades of uncompromised Surat stone cutting.' WHERE id = 3;
  ```

### How to Hide or Show the Section
If the section is inactive, the template suppresses rendering completely (no blank space or gap):
- **Hide the section**:
  ```sql
  UPDATE feature_section SET active = 0 WHERE id = 1;
  ```
- **Show the section**:
  ```sql
  UPDATE feature_section SET active = 1 WHERE id = 1;
  ```

### Asset Verification Tool
Run the automated asset auditor to verify that all images exist on disk, have meaningful alt text, are valid WebPs under size limits, and that the entire section weight remains under the 700 KB budget:
```bash
python tools/check_assets.py
```

### Test Checklist
- [x] **Placement**: Sits strictly before "Four Master Chapters of The Atelier" (Section 3) and after "How a piece is made" (Section 2).
- [x] **Scroll Anchor**: Jumps smoothly to `id="edit"` from navigation links.
- [x] **Edge Blending**: 96px vertical padding; top and bottom edges melt seamlessly into `#25101f` with zero hard lines.
- [x] **Text Contrast**: Cormorant Garamond `#FAF7F2` on `#25101f` plum achieves 13.5:1 contrast (exceeding WCAG AA 4.5:1 and AAA 7:1); mobile scrim ensures AA contrast on small screens.
- [x] **Hexagon Frames**: 3 hexagonal cutouts with 14px champagne (`#ead9b6`) offset outlines fade in once via `IntersectionObserver` on desktop; reduced cleanly on tablet/mobile.
- [x] **Tile Hover**: Subtle 1.04 photo scale with 0.6s easing and button background fill.
- [x] **Responsive Grid**: 12 columns desktop, 6 columns tablet, 1 column mobile (with photos displayed first before text blocks).
- [x] **Missing-Image Fallback**: Flat brand-colour tile with title displayed if any image fails to load.
- [x] **Reduced Motion**: Disables transforms and animations when `prefers-reduced-motion: reduce` is active.
- [x] **Zero Console Errors**: Verified in headless Chrome.
