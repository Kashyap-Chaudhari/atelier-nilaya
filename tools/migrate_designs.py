#!/usr/bin/env python3
"""
Atelier Nilaya â€” Database Migration: The Sketchbook Designs
Adds the 'designs' table to nilaya.db and populates authentic archival design records.
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'nilaya.db')

DESIGNS = [
    {
        'product_slug': 'the-empress-cushion-solitaire-2-2ct',
        'year': 1987,
        'title': 'The Empress Cushion Solitaire',
        'story': 'Drawn in 1987. Still our best-selling bespoke solitaire ring.',
        'sketch_path': '/static/sketches/the-empress-cushion-solitaire.webp',
        'sketch_alt': 'Original 1987 hand-drawn pencil sketch on cream paper of the Empress Cushion Solitaire with workshop bench notes.',
        'sort_order': 1
    },
    {
        'product_slug': 'pink-sapphire-diamond-cocktail-ring',
        'year': 1994,
        'title': 'Pink Sapphire & Diamond Cocktail Ring',
        'story': 'Sketched in 1994 for a private royal commission, featuring a double-tiered micro-pavé halo.',
        'sketch_path': '/static/sketches/pink-sapphire-diamond-cocktail-ring.webp',
        'sketch_alt': 'Original 1994 pencil study of the oval cushion cocktail ring with micro-claw spacing annotations.',
        'sort_order': 2
    },
    {
        'product_slug': 'imperial-navratna-royal-crest-ring',
        'year': 1978,
        'title': 'Imperial Navratna Royal Crest Ring',
        'story': 'Hand-drafted in 1978 to align nine sacred planetary gems in an unbroken concentric gold bezel.',
        'sketch_path': '/static/sketches/imperial-navratna-royal-crest-ring.webp',
        'sketch_alt': '1978 archival pencil draft of the sacred Navratna geometric arrangement with planetary coordinates.',
        'sort_order': 3
    },
    {
        'product_slug': '24k-hand-carved-signet-band',
        'year': 2003,
        'title': '24K Hand-Carved Signet Band',
        'story': 'Conceived in 2003 with architectural chamfers and an ancestral crest shield carved from solid 24K gold.',
        'sketch_path': '/static/sketches/24k-hand-carved-signet-band.webp',
        'sketch_alt': 'Pencil drafting of the heavyweight faceted signet band with millimeter wall thickness callouts.',
        'sort_order': 4
    }
]

def migrate():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS designs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            title TEXT NOT NULL,
            story TEXT NOT NULL,
            sketch_path TEXT NOT NULL,
            sketch_alt TEXT NOT NULL,
            sort_order INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_designs_product ON designs(product_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_designs_order ON designs(sort_order);")

    # Clear existing to ensure clean idempotency
    cur.execute("DELETE FROM designs")

    for d in DESIGNS:
        prod = cur.execute("SELECT id FROM products WHERE slug = ?", (d['product_slug'],)).fetchone()
        if not prod:
            print(f"Warning: Product '{d['product_slug']}' not found in products table.")
            continue
        pid = prod[0]
        cur.execute("""
            INSERT INTO designs (product_id, year, title, story, sketch_path, sketch_alt, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pid, d['year'], d['title'], d['story'], d['sketch_path'], d['sketch_alt'], d['sort_order']))
        print(f"Inserted design: {d['title']} ({d['year']}) -> Product ID {pid}")

    con.commit()
    print("Migration successful: 'designs' table populated.")
    con.close()

if __name__ == '__main__':
    migrate()
