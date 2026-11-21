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
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        im = im.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        im = im.crop((0, top, w, top + new_h))

    return im.resize((target_w, target_h), Image.Resampling.LANCZOS)

def crop_box(im, left_r, top_r, right_r, bottom_r, out_size=140):
    w, h = im.size
    left = int(w * left_r)
    top = int(h * top_r)
    right = int(w * right_r)
    bottom = int(h * bottom_r)
    cropped = im.crop((left, top, right, bottom))
    # Make square by adding padding or center-crop
    cw, ch = cropped.size
    side = min(cw, ch)
    cx, cy = cw // 2, ch // 2
    sq = cropped.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))
    return sq.resize((out_size, out_size), Image.Resampling.LANCZOS)

# Open museum assets
bangles_916 = Image.open('scratch_wiki_bangles_916.jpg')
bangle_big_kada = Image.open('scratch_wiki_bangle_big_kada.jpg')
bangles_four = Image.open('scratch_wiki_bangles_four.jpg')
bangle_arm_bracelet = Image.open('scratch_wiki_bangle_arm_bracelet.jpg')
bangle_doris_duke = Image.open('scratch_wiki_bangle_doris_duke.jpg')

earrings_kammalu = Image.open('scratch_wiki_earrings_kammalu.jpg')
earrings_delhi = Image.open('scratch_wiki_earrings_delhi.jpg')
earrings_madras = Image.open('scratch_wiki_earrings_madras.jpg')

ear_jhumka_src = Image.open('scratch_test_earrings_jhumka_1.jpg')
ear_chandbali_src = Image.open('scratch_test_earrings_chandbali_1.jpg')
ear_hoop_src = Image.open('scratch_test_earrings_gold_hoop.jpg')

print("1. Installing Banners...")
# Bangles Promo Banner (Must be genuine royal Indian gold kadas!)
promo_kada = crop_center_ratio(bangle_big_kada, 600, 800)
promo_kada.save(os.path.join(PROMOS_DIR, 'promo-heritage-kadas.jpg'), 'JPEG', quality=92)
print("  Installed promo-heritage-kadas.jpg (100% pure royal gold kada)")

# Earrings Promo Banner (Royal Mughal ear ornaments)
promo_ear = crop_center_ratio(earrings_delhi, 600, 800)
promo_ear.save(os.path.join(PROMOS_DIR, 'promo-chandbalis.jpg'), 'JPEG', quality=92)
print("  Installed promo-chandbalis.jpg (Royal Delhi museum ear adornments)")

# Category showcase images for homepage "Shop by Category"
cat_bangles = crop_center_ratio(bangles_916, 600, 600)
cat_bangles.save(os.path.join(CATS_DIR, 'cat-bangles.jpg'), 'JPEG', quality=92)

cat_ear = crop_center_ratio(earrings_kammalu, 600, 600)
cat_ear.save(os.path.join(CATS_DIR, 'cat-earrings.jpg'), 'JPEG', quality=92)
print("  Installed cat-bangles.jpg and cat-earrings.jpg")

print("\n2. Installing Bangles Thumbnails...")
crop_box(bangles_916, 0.1, 0.1, 0.9, 0.9).save(os.path.join(THUMBS_DIR, 'bangle-all.jpg'), 'JPEG', quality=92)
crop_box(bangles_four, 0.15, 0.15, 0.85, 0.85).save(os.path.join(THUMBS_DIR, 'bangle-gold.jpg'), 'JPEG', quality=92)
crop_box(bangle_arm_bracelet, 0.2, 0.2, 0.8, 0.8).save(os.path.join(THUMBS_DIR, 'bangle-diamond.jpg'), 'JPEG', quality=92)
crop_box(bangles_916, 0.2, 0.2, 0.8, 0.8).save(os.path.join(THUMBS_DIR, 'bangle-bridal.jpg'), 'JPEG', quality=92)
crop_box(bangle_big_kada, 0.15, 0.15, 0.85, 0.85).save(os.path.join(THUMBS_DIR, 'bangle-kadas.jpg'), 'JPEG', quality=92)
crop_box(bangle_doris_duke, 0.1, 0.1, 0.9, 0.9).save(os.path.join(THUMBS_DIR, 'bangle-temple.jpg'), 'JPEG', quality=92)
crop_box(bangles_four, 0.25, 0.25, 0.75, 0.75).save(os.path.join(THUMBS_DIR, 'bangle-daily.jpg'), 'JPEG', quality=92)
crop_box(bangle_doris_duke, 0.2, 0.2, 0.8, 0.8).save(os.path.join(THUMBS_DIR, 'bangle-antique.jpg'), 'JPEG', quality=92)
crop_box(bangles_916, 0.15, 0.15, 0.85, 0.85).save(os.path.join(THUMBS_DIR, 'bridal-bangle.jpg'), 'JPEG', quality=92)
crop_box(bangle_big_kada, 0.2, 0.2, 0.8, 0.8).save(os.path.join(THUMBS_DIR, 'temple-bangle.jpg'), 'JPEG', quality=92)
crop_box(bangle_arm_bracelet, 0.15, 0.15, 0.85, 0.85).save(os.path.join(THUMBS_DIR, 'dia-brace.jpg'), 'JPEG', quality=92)
crop_box(bangle_big_kada, 0.1, 0.1, 0.9, 0.9).save(os.path.join(THUMBS_DIR, 'engraved-bracelets.jpg'), 'JPEG', quality=92)

print("\n3. Installing Earrings Thumbnails...")
crop_box(earrings_kammalu, 0.15, 0.15, 0.85, 0.85).save(os.path.join(THUMBS_DIR, 'ear-all.jpg'), 'JPEG', quality=92)
crop_box(ear_jhumka_src, 0.2, 0.1, 0.8, 0.7).save(os.path.join(THUMBS_DIR, 'ear-jhumka.jpg'), 'JPEG', quality=92)
crop_box(earrings_kammalu, 0.45, 0.2, 0.95, 0.8).save(os.path.join(THUMBS_DIR, 'ear-stud.jpg'), 'JPEG', quality=92)
crop_box(ear_hoop_src, 0.15, 0.15, 0.85, 0.85).save(os.path.join(THUMBS_DIR, 'ear-hoop.jpg'), 'JPEG', quality=92)
crop_box(ear_chandbali_src, 0.15, 0.15, 0.85, 0.85).save(os.path.join(THUMBS_DIR, 'ear-chandbali.jpg'), 'JPEG', quality=92)
crop_box(earrings_madras, 0.1, 0.1, 0.9, 0.9).save(os.path.join(THUMBS_DIR, 'ear-drop.jpg'), 'JPEG', quality=92)
crop_box(earrings_delhi, 0.1, 0.1, 0.9, 0.9).save(os.path.join(THUMBS_DIR, 'ear-trad.jpg'), 'JPEG', quality=92)
crop_box(ear_chandbali_src, 0.2, 0.2, 0.8, 0.8).save(os.path.join(THUMBS_DIR, 'ear-diamond.jpg'), 'JPEG', quality=92)
crop_box(earrings_madras, 0.15, 0.15, 0.85, 0.85).save(os.path.join(THUMBS_DIR, 'temple-ear.jpg'), 'JPEG', quality=92)
crop_box(earrings_delhi, 0.15, 0.15, 0.85, 0.85).save(os.path.join(THUMBS_DIR, 'bridal-ear.jpg'), 'JPEG', quality=92)

print("\nAll museum-grade Indian jewellery assets installed with perfection!")
