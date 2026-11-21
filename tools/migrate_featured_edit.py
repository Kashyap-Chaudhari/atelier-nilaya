import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'nilaya.db')
db = sqlite3.connect(DB_PATH)
cur = db.cursor()

print("Applying safe Featured Edit migration to nilaya.db...")

# 1. Drop existing tables safely to rebuild with exact schema
cur.execute("DROP TABLE IF EXISTS feature_tiles;")
cur.execute("DROP TABLE IF EXISTS feature_section;")

# 2. Create feature_section table
cur.execute("""
CREATE TABLE feature_section (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    button_text TEXT NOT NULL,
    button_link TEXT NOT NULL,
    bg_image_path TEXT NOT NULL,
    bg_alt TEXT NOT NULL,
    hex_1_path TEXT,
    hex_1_alt TEXT,
    hex_2_path TEXT,
    hex_2_alt TEXT,
    hex_3_path TEXT,
    hex_3_alt TEXT,
    active INTEGER DEFAULT 1
);
""")

# 3. Create feature_tiles table
cur.execute("""
CREATE TABLE feature_tiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_section_id INTEGER NOT NULL,
    sort_order INTEGER DEFAULT 1,
    kind TEXT NOT NULL, -- 'photo', 'product_group', 'text_block'
    title TEXT,
    body TEXT,
    button_text TEXT,
    link TEXT,
    image_path TEXT,
    image_alt TEXT,
    bg_color TEXT,
    product_ids TEXT,   -- Comma-separated product IDs (e.g. '1,2,3,4') for product_group
    active INTEGER DEFAULT 1,
    FOREIGN KEY (feature_section_id) REFERENCES feature_section(id) ON DELETE CASCADE
);
""")

cur.execute("CREATE INDEX IF NOT EXISTS idx_feature_section_active ON feature_section(active);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_feature_tiles_section ON feature_tiles(feature_section_id, sort_order);")

# 4. Insert section record with real copy and paths
cur.execute("""
INSERT INTO feature_section (
    id, title, body, button_text, button_link,
    bg_image_path, bg_alt,
    hex_1_path, hex_1_alt,
    hex_2_path, hex_2_alt,
    hex_3_path, hex_3_alt,
    active
) VALUES (
    1,
    'Calibrated diamond fire and ancestral 24-karat gold forged for the autumn season.',
    'Every archival creation is weighed by hand on Surat historic lapidary benches to reflect light from every vantage.',
    'EXPLORE THE EDIT',
    '/c/rings',
    '/static/lifestyle/hero-lifestyle-1920.webp',
    'Model wearing royal solitaire jewellery and pure gold neckwear',
    '/static/lifestyle/hex-1-ring.webp',
    'Close-up of hand-set solitaire cushion diamond ring',
    '/static/lifestyle/hex-2-earrings.webp',
    'Model wearing chandelier diamond drop earrings',
    '/static/lifestyle/hex-3-necklace.webp',
    'Model wearing handcrafted polki choker necklace',
    1
);
""")

# 5. Insert 7 feature tiles (between 6 and 8 tiles)
tiles = [
    # 1. Full-bleed lifestyle photo (Span 5 on desktop)
    (
        1, 1, 'photo',
        'Heirloom Solitaire Styling', None, None, '/c/necklaces',
        '/static/lifestyle/lifestyle-product-1.webp',
        'Full-bleed portrait wearing handcrafted heirloom jewellery in morning light',
        None, None, 1
    ),
    # 2. 2x2 group of four product tiles on light grey #f6f6f6 (Span 7 on desktop)
    (
        1, 2, 'product_group',
        'CURATED ACQUISITIONS', None, 'VIEW VAULT', '/c/rings',
        None, None, '#f6f6f6', '1,2,3,4', 1
    ),
    # 3. Taupe text block (Span 4 on desktop)
    (
        1, 3, 'text_block',
        'THE ATELIER MANIFESTO',
        'Every gemstone in our vault is calibrated by eye and weighed by hand on Surat historic lapidary benches. We forge heirloom pieces that hold their character across centuries.',
        'OUR CRAFTSMANSHIP', '/#craftsmanship',
        None, None, '#7d6b57', None, 1
    ),
    # 4. Cream text block (Span 4 on desktop)
    (
        1, 4, 'text_block',
        'BESPOKE VAULT COMMISSIONS',
        'Commission private bridal trousseaus, ancestral signet bands, or rare cushion solitaires directly with our hereditary master karigars.',
        'REQUEST PRIVATE VIEWING', '#private-appointment',
        None, None, '#efeae4', None, 1
    ),
    # 5. Lifestyle photo (Span 4 on desktop)
    (
        1, 5, 'photo',
        'Royal Earring Suite', None, None, '/c/earrings',
        '/static/lifestyle/lifestyle-product-2.webp',
        'Model wearing emerald and diamond chandelier earrings',
        None, None, 1
    )
]

cur.executemany("""
INSERT INTO feature_tiles (
    feature_section_id, sort_order, kind, title, body, button_text, link,
    image_path, image_alt, bg_color, product_ids, active
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
""", tiles)

db.commit()
print(f"✓ Migration successful: 1 feature_section and {len(tiles)} feature_tiles seeded in nilaya.db.")
db.close()
