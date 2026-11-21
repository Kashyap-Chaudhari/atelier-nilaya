import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THUMBS_DIR = os.path.join(BASE_DIR, 'static', 'campaigns', 'img', 'menu', 'thumbnails')
PROMOS_DIR = os.path.join(BASE_DIR, 'static', 'campaigns', 'img', 'menu', 'promos')
CATS_DIR = os.path.join(BASE_DIR, 'static', 'campaigns', 'img', 'categories')

def crop_center_ratio(im, target_w, target_h):
    w, h = im.size
    target_ratio = target_w / target_h
    current_ratio = w / h

    if current_ratio > target_ratio:
        # Image is too wide
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:
        # Image is too tall
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        im = im.crop((0, top, w, top + new_h))

    return im.resize((target_w, target_h), Image.Resampling.LANCZOS)

def crop_square(im, cx_ratio=0.5, cy_ratio=0.5, size_ratio=0.75, out_size=140):
    w, h = im.size
    crop_size = int(min(w, h) * size_ratio)
    cx = int(w * cx_ratio)
    cy = int(h * cy_ratio)
    left = max(0, min(w - crop_size, cx - crop_size // 2))
    top = max(0, min(h - crop_size, cy - crop_size // 2))
    cropped = im.crop((left, top, left + crop_size, top + crop_size))
    return cropped.resize((out_size, out_size), Image.Resampling.LANCZOS)

# 1. Load newly downloaded images
bangles_1 = Image.open('scratch_test_bangles_gold_1.jpg')
bangles_2 = Image.open('scratch_test_bangles_gold_2.jpg')
bangles_3 = Image.open('scratch_test_bangles_gold_3.jpg')
bangles_4 = Image.open('scratch_test_bangles_gold_4.jpg')

ear_jhumka = Image.open('scratch_test_earrings_jhumka_1.jpg')
ear_studs = Image.open('scratch_test_earrings_studs_1.jpg')
ear_chandbali = Image.open('scratch_test_earrings_chandbali_1.jpg')
ear_hoop = Image.open('scratch_test_earrings_gold_hoop.jpg')
ear_trad = Image.open('scratch_test_earrings_trad_1.jpg')

ring_solitaire = Image.open('scratch_test_ring_solitaire.jpg')
ring_cocktail = Image.open('scratch_test_ring_cocktail.jpg')
ring_band = Image.open('scratch_test_ring_gold_band.jpg')

print("1. Replacing Promotional Banners...")
# Promo banner for Bangles (MUST BE REAL GOLD BANGLES, NOT A PINK RING!)
promo_kadas = crop_center_ratio(bangles_1, 600, 800)
promo_kadas.save(os.path.join(PROMOS_DIR, 'promo-heritage-kadas.jpg'), 'JPEG', quality=90)
print("  Saved promo-heritage-kadas.jpg (Real gold bangles)")

# Promo banner for Earrings (Chandbalis)
promo_chandbali = crop_center_ratio(ear_chandbali, 600, 800)
promo_chandbali.save(os.path.join(PROMOS_DIR, 'promo-chandbalis.jpg'), 'JPEG', quality=90)
print("  Saved promo-chandbalis.jpg (Real Indian chandbalis)")

print("\n2. Replacing Category Card Banners in Shop by Category...")
crop_center_ratio(bangles_1, 600, 600).save(os.path.join(CATS_DIR, 'cat-bangles.jpg'), 'JPEG', quality=92)
crop_center_ratio(ear_chandbali, 600, 600).save(os.path.join(CATS_DIR, 'cat-earrings.jpg'), 'JPEG', quality=92)
print("  Saved cat-bangles.jpg & cat-earrings.jpg")

print("\n3. Generating Authentic Bangle Thumbnails (Zero rings!)...")
crop_square(bangles_1, 0.5, 0.45, 0.7).save(os.path.join(THUMBS_DIR, 'bangle-all.jpg'), 'JPEG', quality=92)
crop_square(bangles_2, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'bangle-gold.jpg'), 'JPEG', quality=92)
crop_square(bangles_3, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'bangle-diamond.jpg'), 'JPEG', quality=92)
crop_square(bangles_1, 0.45, 0.6, 0.65).save(os.path.join(THUMBS_DIR, 'bangle-bridal.jpg'), 'JPEG', quality=92)
crop_square(bangles_4, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'bangle-kadas.jpg'), 'JPEG', quality=92)
crop_square(bangles_1, 0.55, 0.35, 0.65).save(os.path.join(THUMBS_DIR, 'bangle-temple.jpg'), 'JPEG', quality=92)
crop_square(bangles_2, 0.4, 0.5, 0.7).save(os.path.join(THUMBS_DIR, 'bangle-daily.jpg'), 'JPEG', quality=92)
crop_square(bangles_4, 0.6, 0.5, 0.7).save(os.path.join(THUMBS_DIR, 'bangle-antique.jpg'), 'JPEG', quality=92)
crop_square(bangles_1, 0.5, 0.5, 0.7).save(os.path.join(THUMBS_DIR, 'bridal-bangle.jpg'), 'JPEG', quality=92)
crop_square(bangles_1, 0.5, 0.5, 0.7).save(os.path.join(THUMBS_DIR, 'temple-bangle.jpg'), 'JPEG', quality=92)
crop_square(bangles_3, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'dia-brace.jpg'), 'JPEG', quality=92)
crop_square(bangles_4, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'engraved-bracelets.jpg'), 'JPEG', quality=92)

print("\n4. Generating Authentic Earring Thumbnails (Distinct styles!)...")
crop_square(ear_chandbali, 0.5, 0.5, 0.75).save(os.path.join(THUMBS_DIR, 'ear-all.jpg'), 'JPEG', quality=92)
crop_square(ear_jhumka, 0.5, 0.4, 0.7).save(os.path.join(THUMBS_DIR, 'ear-jhumka.jpg'), 'JPEG', quality=92)
crop_square(ear_studs, 0.5, 0.4, 0.65).save(os.path.join(THUMBS_DIR, 'ear-stud.jpg'), 'JPEG', quality=92)
crop_square(ear_hoop, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'ear-hoop.jpg'), 'JPEG', quality=92)
crop_square(ear_chandbali, 0.5, 0.4, 0.65).save(os.path.join(THUMBS_DIR, 'ear-chandbali.jpg'), 'JPEG', quality=92)
crop_square(ear_studs, 0.5, 0.6, 0.65).save(os.path.join(THUMBS_DIR, 'ear-drop.jpg'), 'JPEG', quality=92)
crop_square(ear_trad, 0.4, 0.5, 0.7).save(os.path.join(THUMBS_DIR, 'ear-trad.jpg'), 'JPEG', quality=92)
crop_square(ear_chandbali, 0.5, 0.6, 0.65).save(os.path.join(THUMBS_DIR, 'ear-diamond.jpg'), 'JPEG', quality=92)
crop_square(ear_jhumka, 0.5, 0.5, 0.7).save(os.path.join(THUMBS_DIR, 'bridal-ear.jpg'), 'JPEG', quality=92)
crop_square(ear_trad, 0.5, 0.5, 0.7).save(os.path.join(THUMBS_DIR, 'temple-ear.jpg'), 'JPEG', quality=92)

print("\n5. Generating Authentic Ring Thumbnails...")
crop_square(ring_solitaire, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'ring-all.jpg'), 'JPEG', quality=92)
crop_square(ring_solitaire, 0.5, 0.45, 0.7).save(os.path.join(THUMBS_DIR, 'ring-engage.jpg'), 'JPEG', quality=92)
crop_square(ring_band, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'ring-bands.jpg'), 'JPEG', quality=92)
crop_square(ring_solitaire, 0.5, 0.5, 0.7).save(os.path.join(THUMBS_DIR, 'ring-diamond.jpg'), 'JPEG', quality=92)
crop_square(ring_band, 0.45, 0.45, 0.75).save(os.path.join(THUMBS_DIR, 'ring-gold.jpg'), 'JPEG', quality=92)
crop_square(ring_cocktail, 0.5, 0.5, 0.75).save(os.path.join(THUMBS_DIR, 'ring-cocktail.jpg'), 'JPEG', quality=92)
crop_square(ring_band, 0.55, 0.55, 0.75).save(os.path.join(THUMBS_DIR, 'ring-couple.jpg'), 'JPEG', quality=92)
crop_square(ring_band, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'ring-mens.jpg'), 'JPEG', quality=92)
crop_square(ring_band, 0.5, 0.5, 0.8).save(os.path.join(THUMBS_DIR, 'pers-rings.jpg'), 'JPEG', quality=92)
crop_square(ring_solitaire, 0.5, 0.5, 0.75).save(os.path.join(THUMBS_DIR, 'bridal-rings.jpg'), 'JPEG', quality=92)

print("\nAll authentic photography cropped and installed successfully!")
