#!/usr/bin/env python3
"""
Safe Migration Script: Adds product_images table and products.spin_frames column.
Safe to run multiple times without data loss.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nilaya.db')

def migrate():
    print(f"Connecting to database: {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # 1. Check and add spin_frames column to products if missing
    cur.execute("PRAGMA table_info(products)")
    existing_cols = [c[1] for c in cur.fetchall()]
    
    if 'spin_frames' not in existing_cols:
        print("Adding column 'spin_frames' to products table...")
        cur.execute("ALTER TABLE products ADD COLUMN spin_frames INTEGER DEFAULT 36")
    else:
        print("Column 'spin_frames' already exists in products.")

    # 2. Create product_images table if missing
    print("Creating product_images table if it does not exist...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            metal TEXT NOT NULL,
            kind TEXT NOT NULL CHECK(kind IN ('spin', 'front', 'side', 'top', 'lifestyle')),
            frame_index INTEGER,
            path TEXT NOT NULL,
            alt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)

    # 3. Create indexes
    print("Creating indexes on product_images...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_product_images_lookup ON product_images(product_id, metal, kind)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug)")

    con.commit()
    con.close()
    print("Migration completed successfully.")

if __name__ == '__main__':
    migrate()
