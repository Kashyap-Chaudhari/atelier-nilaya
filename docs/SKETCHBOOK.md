# The Sketchbook: From Pencil to Jewel

Guide for digitizing archival jewelry design sketches, adding new designs to the catalog, and linking them to real workshop products in Atelier Nilaya.

---

## 1. How to Scan or Photograph a Design Sketch

To achieve a seamless before-and-after blend where dragging the divider feels like the pencil drawing is turning into the finished jewel:

1. **Camera / Scanner Alignment**:
   - Place the sketchbook on a flat drafting surface.
   - Use a camera or book scanner positioned strictly parallel ($90^\circ$ perpendicular) to the paper to prevent perspective distortion or keystone skewing.
2. **Lighting**:
   - Use two balanced, diffused $5000\text{K}$ daylight light sources at $45^\circ$ angles from opposite sides.
   - Strictly zero direct flash and zero directional harsh shadows.
3. **Resolution & Crop**:
   - Scan or shoot at **$2000\text{px}$ wide** or higher at 300 DPI.
   - Crop the sketch so the piece's center axis and scale match the product photo front view (`static/products/<slug>/<metal>/front.webp`).
4. **Export Format**:
   - Convert to WebP format at $88\%$ quality.
   - Target file size: under $80\text{ KB}$.
   - Save to: `static/sketches/<design-slug>.webp`.

---

## 2. How to Add a New Design

Designs are stored in the `designs` database table in `nilaya.db`.

### SQL Insertion Example:
```sql
INSERT INTO designs (
    product_id,
    year,
    title,
    story,
    sketch_path,
    sketch_alt,
    sort_order
) VALUES (
    1,                                                         -- Matching product id in `products` table
    1987,                                                      -- Year sketched
    'The Empress Cushion Solitaire',                          -- Piece title
    'Drawn in 1987. Still our best-selling bespoke solitaire ring.', -- One sentence founder story
    '/static/sketches/the-empress-cushion-solitaire.webp',    -- WebP sketch path
    'Original 1987 pencil sketch on cream paper of the Empress Cushion Solitaire.',
    1                                                          -- Display sort order
);
```

---

## 3. How to Link a Design to a Real Product

1. **Verify Matching Product**:
   Ensure `product_id` corresponds to an existing row in `products`.
2. **Verify Product Imagery in `product_images`**:
   The right side of the slider loads the authentic product from `product_images`:
   - `spin` frames (`001.webp` to `036.webp`)
   - `front.webp` still
   - Metal variants (`yellow_gold`, `rose_gold`, `platinum`, `silver`)
3. **Run Asset Auditor**:
   Run the automated checker:
   ```bash
   python tools/check_assets.py
   ```
   The script verifies that every design has its sketch file, a valid linked product, and all finished views on disk.
