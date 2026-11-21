import os
import urllib.request
from PIL import Image, ImageOps

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THUMBS_DIR = os.path.join(BASE_DIR, 'static', 'campaigns', 'img', 'menu', 'thumbnails')
PROMOS_DIR = os.path.join(BASE_DIR, 'static', 'campaigns', 'img', 'menu', 'promos')

os.makedirs(THUMBS_DIR, exist_ok=True)
os.makedirs(PROMOS_DIR, exist_ok=True)

# Curated High-Definition Unsplash Jewellery Photography
IMAGE_SOURCES = {
    # Promotional Banners (Portrait 600x800)
    'promo_new_collection': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&q=85',
    'promo_generations': 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=85',
    'promo_royal_chokers': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&q=85',
    'promo_chandbalis': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&q=85',
    'promo_solitaire_rings': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&q=85',
    'promo_cocktail_rings': 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800&q=85',
    'promo_heritage_kadas': 'https://images.unsplash.com/photo-1611591475880-9285038c11ec?w=800&q=85',
    'promo_bridal_edit': 'https://images.unsplash.com/photo-1583939003579-730e3918a45a?w=800&q=85',
    'promo_sacred_temple': 'https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?w=800&q=85',
    'promo_diamond_atelier': 'https://images.unsplash.com/photo-1600003014755-ba31aa59c4b6?w=800&q=85',
    'promo_heirloom_gifting': 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=800&q=85',
    'promo_mens_jewellery': 'https://images.unsplash.com/photo-1506630448388-4e683c67ddb0?w=800&q=85',
    
    # Specific Jewelry Items for Circular Thumbnails
    'item_diamond_ring': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80',
    'item_gold_ring': 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=500&q=80',
    'item_cocktail_ring': 'https://images.unsplash.com/photo-1598560917505-59a3ad559071?w=500&q=80',
    'item_necklace_gold': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&q=80',
    'item_necklace_diamond': 'https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=500&q=80',
    'item_earring_drop': 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80',
    'item_earring_pearl': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&q=80',
    'item_bangle_gold': 'https://images.unsplash.com/photo-1611591475880-9285038c11ec?w=500&q=80',
    'item_pendant': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&q=80',
    'item_temple': 'https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?w=500&q=80',
    'item_bridal': 'https://images.unsplash.com/photo-1583939003579-730e3918a45a?w=500&q=80',
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

raw_cache = {}

print("Downloading reference photography...")
for key, url in IMAGE_SOURCES.items():
    raw_path = os.path.join(BASE_DIR, 'scratch_' + key + '.jpg')
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp, open(raw_path, 'wb') as out_f:
            out_f.write(resp.read())
        raw_cache[key] = raw_path
        print(f"Downloaded {key}")
    except Exception as e:
        print(f"Failed {key}: {e}")

# Process Promotional Banners (600x800, subtle crop)
PROMO_MAPPINGS = {
    'promo-new-collection.jpg': 'promo_new_collection',
    'promo-generations.jpg': 'promo_generations',
    'promo-royal-chokers.jpg': 'promo_royal_chokers',
    'promo-chandbalis.jpg': 'promo_chandbalis',
    'promo-solitaire-rings.jpg': 'promo_solitaire_rings',
    'promo-cocktail-rings.jpg': 'promo_cocktail_rings',
    'promo-heritage-kadas.jpg': 'promo_heritage_kadas',
    'promo-bridal-edit.jpg': 'promo_bridal_edit',
    'promo-sacred-temple.jpg': 'promo_sacred_temple',
    'promo-diamond-atelier.jpg': 'promo_diamond_atelier',
    'promo-heirloom-gifting.jpg': 'promo_heirloom_gifting',
    'promo-mens-jewellery.jpg': 'promo_mens_jewellery',
}

for filename, source_key in PROMO_MAPPINGS.items():
    out_path = os.path.join(PROMOS_DIR, filename)
    src_file = raw_cache.get(source_key)
    if src_file and os.path.exists(src_file):
        im = Image.open(src_file)
        # Crop center to 600x800 aspect ratio
        w, h = im.size
        target_ratio = 600 / 800
        current_ratio = w / h
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            im = im.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            im = im.crop((0, top, w, top + new_h))
        im = im.resize((600, 800), Image.Resampling.LANCZOS)
        im.save(out_path, 'JPEG', quality=88)
        print(f"Saved banner: {filename}")

# Process Circular Thumbnails (140x140 square for crisp 48px rendering on retina screens)
# Thumbnails have a soft ivory background (#F7F2E9) with the jewelry centered inside
THUMB_MAPPINGS = {
    'new-in.jpg': 'item_gold_ring',
    'bestsellers.jpg': 'item_necklace_gold',
    'festive.jpg': 'item_temple',
    'wedding.jpg': 'item_bridal',
    'everyday.jpg': 'item_diamond_ring',
    'exclusive.jpg': 'item_cocktail_ring',
    'gift-sets.jpg': 'item_necklace_diamond',
    'latest.jpg': 'item_earring_drop',
    'bridal-col.jpg': 'item_bridal',
    'heritage-col.jpg': 'item_temple',
    'diamond-col.jpg': 'item_necklace_diamond',
    'temple-col.jpg': 'item_temple',
    'customer-fav.jpg': 'item_gold_ring',
    'designer.jpg': 'item_earring_pearl',
    'trending.jpg': 'item_bangle_gold',
    'special-occ.jpg': 'item_cocktail_ring',
    'custom-necklace.jpg': 'item_necklace_gold',
    'initial-pendant.jpg': 'item_pendant',
    'pers-rings.jpg': 'item_diamond_ring',
    'engraved-bracelets.jpg': 'item_bangle_gold',
    'custom-bridal.jpg': 'item_bridal',
    'design-own.jpg': 'item_cocktail_ring',
    # Necklaces
    'neck-all.jpg': 'item_necklace_gold',
    'neck-gold.jpg': 'item_necklace_gold',
    'neck-diamond.jpg': 'item_necklace_diamond',
    'neck-bridal.jpg': 'item_bridal',
    'neck-temple.jpg': 'item_temple',
    'neck-choker.jpg': 'item_necklace_gold',
    'neck-long.jpg': 'item_necklace_diamond',
    'neck-pendant.jpg': 'item_pendant',
    'style-trad.jpg': 'item_temple',
    'style-contemp.jpg': 'item_diamond_ring',
    'style-antique.jpg': 'item_temple',
    'style-minimal.jpg': 'item_gold_ring',
    'style-kundan.jpg': 'item_bridal',
    'style-polki.jpg': 'item_necklace_gold',
    'style-pearl.jpg': 'item_earring_pearl',
    'style-statement.jpg': 'item_cocktail_ring',
    # Earrings
    'ear-all.jpg': 'item_earring_drop',
    'ear-jhumka.jpg': 'item_temple',
    'ear-stud.jpg': 'item_diamond_ring',
    'ear-hoop.jpg': 'item_bangle_gold',
    'ear-chandbali.jpg': 'item_bridal',
    'ear-drop.jpg': 'item_earring_drop',
    'ear-trad.jpg': 'item_temple',
    'ear-diamond.jpg': 'item_necklace_diamond',
    # Rings
    'ring-all.jpg': 'item_diamond_ring',
    'ring-engage.jpg': 'item_diamond_ring',
    'ring-bands.jpg': 'item_gold_ring',
    'ring-diamond.jpg': 'item_diamond_ring',
    'ring-gold.jpg': 'item_gold_ring',
    'ring-cocktail.jpg': 'item_cocktail_ring',
    'ring-couple.jpg': 'item_gold_ring',
    'ring-mens.jpg': 'item_gold_ring',
    # Bangles
    'bangle-all.jpg': 'item_bangle_gold',
    'bangle-gold.jpg': 'item_bangle_gold',
    'bangle-diamond.jpg': 'item_necklace_diamond',
    'bangle-bridal.jpg': 'item_bridal',
    'bangle-kadas.jpg': 'item_bangle_gold',
    'bangle-temple.jpg': 'item_temple',
    'bangle-daily.jpg': 'item_gold_ring',
    'bangle-antique.jpg': 'item_temple',
    # Bridal
    'bridal-sets.jpg': 'item_bridal',
    'bridal-neck.jpg': 'item_necklace_gold',
    'bridal-ear.jpg': 'item_earring_drop',
    'bridal-bangle.jpg': 'item_bangle_gold',
    'bridal-tikka.jpg': 'item_bridal',
    'bridal-nath.jpg': 'item_gold_ring',
    'bridal-rings.jpg': 'item_cocktail_ring',
    # Temple
    'temple-all.jpg': 'item_temple',
    'temple-neck.jpg': 'item_temple',
    'temple-ear.jpg': 'item_temple',
    'temple-bangle.jpg': 'item_bangle_gold',
    'temple-pendant.jpg': 'item_pendant',
    'temple-bridal.jpg': 'item_bridal',
    # Diamond
    'dia-neck.jpg': 'item_necklace_diamond',
    'dia-ring.jpg': 'item_diamond_ring',
    'dia-ear.jpg': 'item_earring_drop',
    'dia-brace.jpg': 'item_bangle_gold',
    'dia-pendant.jpg': 'item_pendant',
    'dia-bridal.jpg': 'item_bridal',
}

for filename, source_key in THUMB_MAPPINGS.items():
    out_path = os.path.join(THUMBS_DIR, filename)
    src_file = raw_cache.get(source_key)
    if src_file and os.path.exists(src_file):
        im = Image.open(src_file)
        w, h = im.size
        # Square crop
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        im_crop = im.crop((left, top, left + min_dim, top + min_dim))
        im_thumb = im_crop.resize((140, 140), Image.Resampling.LANCZOS)
        im_thumb.save(out_path, 'JPEG', quality=90)
    else:
        print(f"Missing source for {filename}")

# Clean temporary scratch files
for key, p in raw_cache.items():
    if os.path.exists(p):
        try:
            os.remove(p)
        except:
            pass

print("Asset processing complete!")
