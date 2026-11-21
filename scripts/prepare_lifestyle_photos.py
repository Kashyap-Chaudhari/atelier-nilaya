import os
import sqlite3
from PIL import Image

STATIC_DIR = "static"
LIFESTYLE_DIR = os.path.join(STATIC_DIR, "lifestyle")
os.makedirs(LIFESTYLE_DIR, exist_ok=True)

def crop_center_square(img):
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    return img.crop((left, top, left + min_dim, top + min_dim)).resize((600, 600), Image.Resampling.LANCZOS)

# Map products to appropriate lifestyle source images and metadata
PRODUCT_METADATA = {
    1: { # The Empress Cushion Solitaire (2.2ct)
        "source": "static/campaigns/img/menu/promos/promo-solitaire-rings.jpg",
        "body_part": "hand",
        "tag": "BEST SELLER",
        "old_price": 720000.0, # 10% discount: Save 10%
        "stone_type": "solitaire",
        "occasion": "bridal"
    },
    2: { # Pink Sapphire & Diamond Cocktail Ring
        "source": "static/campaigns/img/menu/promos/promo-cocktail-rings.jpg",
        "body_part": "hand",
        "tag": "NEW",
        "old_price": 330000.0, # Save 11%
        "stone_type": "sapphire",
        "occasion": "ceremony"
    },
    3: { # Imperial Navratna Royal Crest Ring
        "source": "static/campaigns/img/menu/thumbnails/ring-cocktail.jpg",
        "body_part": "hand",
        "tag": None,
        "old_price": None,
        "stone_type": "navratna",
        "occasion": "heritage"
    },
    4: { # 24K Hand-Carved Signet Band
        "source": "static/campaigns/img/menu/thumbnails/ring-gold.jpg",
        "body_part": "hand",
        "tag": "NEW",
        "old_price": 105000.0, # Save 10%
        "stone_type": "diamond",
        "occasion": "everyday"
    },
    5: { # Eternity Brilliant Diamond Wedding Band
        "source": "static/campaigns/img/menu/thumbnails/ring-bands.jpg",
        "body_part": "hand",
        "tag": "BEST SELLER",
        "old_price": None,
        "stone_type": "diamond",
        "occasion": "bridal"
    },
    6: { # Dual-Tone Platinum & Gold Band
        "source": "static/campaigns/img/menu/thumbnails/ring-couple.jpg",
        "body_part": "hand",
        "tag": None,
        "old_price": 155000.0, # Save 10%
        "stone_type": "solitaire",
        "occasion": "everyday"
    },
    7: { # Imperial Chandelier Chandbalis
        "source": "static/campaigns/img/menu/promos/promo-chandbalis.jpg",
        "body_part": "ear",
        "tag": "BEST SELLER",
        "old_price": 185000.0, # Save 11%
        "stone_type": "polki",
        "occasion": "bridal"
    },
    8: { # Temple Dome Jhumkas in 24K Gold
        "source": "static/campaigns/img/menu/thumbnails/ear-jhumka.jpg",
        "body_part": "ear",
        "tag": None,
        "old_price": None,
        "stone_type": "pearl",
        "occasion": "heritage"
    },
    9: { # Solitaire Diamond Studs (1.8ct TW)
        "source": "static/campaigns/img/menu/thumbnails/ear-stud.jpg",
        "body_part": "ear",
        "tag": "BEST SELLER",
        "old_price": 235000.0, # Save 11%
        "stone_type": "solitaire",
        "occasion": "everyday"
    },
    10: { # Emerald Drop Lotus Danglers
        "source": "static/campaigns/img/categories/cat-earrings.jpg",
        "body_part": "ear",
        "tag": "NEW",
        "old_price": None,
        "stone_type": "emerald",
        "occasion": "ceremony"
    },
    11: { # Imperial Navratna Choker Suite
        "source": "static/campaigns/img/categories/cat-necklaces.jpg",
        "body_part": "neck",
        "tag": "BEST SELLER",
        "old_price": 425000.0, # Save 9%
        "stone_type": "navratna",
        "occasion": "heritage"
    },
    12: { # Basra Pearl & Emerald Rani Haar
        "source": "static/campaigns/img/menu/promos/promo-royal-chokers.jpg",
        "body_part": "neck",
        "tag": "NEW",
        "old_price": None,
        "stone_type": "emerald",
        "occasion": "bridal"
    },
    13: { # Solitaire Diamond Y-Drop Necklace
        "source": "static/campaigns/img/menu/thumbnails/dia-neck.jpg",
        "body_part": "neck",
        "tag": None,
        "old_price": 305000.0, # Save 10%
        "stone_type": "solitaire",
        "occasion": "ceremony"
    },
    14: { # Imperial Makara Head Kada in 22K Gold
        "source": "static/campaigns/img/menu/promos/promo-heritage-kadas.jpg",
        "body_part": "wrist",
        "tag": "BEST SELLER",
        "old_price": None,
        "stone_type": "polki",
        "occasion": "heritage"
    },
    15: { # Diamond Infinity Tennis Bracelet
        "source": "static/campaigns/img/categories/cat-bangles.jpg",
        "body_part": "wrist",
        "tag": "NEW",
        "old_price": 385000.0, # Save 10%
        "stone_type": "diamond",
        "occasion": "everyday"
    },
    16: { # Temple Nakashi Lakshmi Kada Pair
        "source": "static/campaigns/img/menu/thumbnails/bangle-temple.jpg",
        "body_part": "wrist",
        "tag": None,
        "old_price": 400000.0, # Save 10%
        "stone_type": "emerald",
        "occasion": "bridal"
    },
}

conn = sqlite3.connect("nilaya.db")
cur = conn.cursor()

for pid, meta in PRODUCT_METADATA.items():
    src = meta["source"]
    dest_filename = f"lifestyle-product-{pid}.webp"
    dest_path = os.path.join(LIFESTYLE_DIR, dest_filename)
    web_url = f"/static/lifestyle/{dest_filename}"
    
    if os.path.exists(src):
        try:
            with Image.open(src) as img:
                cropped = crop_center_square(img)
                cropped.save(dest_path, "WEBP", quality=88)
                print(f"Created {dest_path} from {src}")
        except Exception as e:
            print(f"Error processing {src}: {e}")
            web_url = None
    else:
        print(f"Warning: {src} does not exist")
        web_url = None

    cur.execute("""
        UPDATE products 
        SET lifestyle_photo = ?,
            lifestyle_body_part = ?,
            tag = ?,
            old_price = ?,
            stone_type = ?,
            occasion = ?
        WHERE id = ?
    """, (
        web_url,
        meta["body_part"],
        meta["tag"],
        meta["old_price"],
        meta["stone_type"],
        meta["occasion"],
        pid
    ))

conn.commit()
print("All products successfully updated with lifestyle photos and metadata!")
