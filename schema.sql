-- ============================================================================
-- ATELIER NILAYA (Surat, India) — DATABASE SCHEMA
-- Luxury Fine Jewellery E-Commerce Database System
-- ============================================================================

-- 1. Jewellery Categories
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    sentence TEXT,
    description TEXT,
    display_order INTEGER DEFAULT 1
);

-- 2. Jewellery Products
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    price REAL NOT NULL,
    base_metal TEXT NOT NULL DEFAULT 'yellow_gold',
    purity TEXT NOT NULL DEFAULT '22K Gold',
    approx_weight TEXT NOT NULL DEFAULT '10.0 g',
    stone TEXT NOT NULL DEFAULT 'Natural Diamond',
    stone_color TEXT DEFAULT '#ffffff',
    certificate TEXT DEFAULT 'BIS 916 Hallmark',
    description TEXT,
    model_type TEXT DEFAULT 'ring',
    glb_file TEXT,
    image_fallback TEXT,
    is_featured BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_webp TEXT,
    old_price REAL,
    tag TEXT,
    occasion TEXT,
    stone_type TEXT,
    lifestyle_photo TEXT,
    lifestyle_body_part TEXT DEFAULT 'hand',
    spin_frames INTEGER DEFAULT 36,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- 3. Product Metal Variants & Pricing
CREATE TABLE IF NOT EXISTS product_metals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    metal TEXT NOT NULL,
    price REAL NOT NULL,
    in_stock BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE(product_id, metal)
);

-- 4. Product Photographic Image System (Replaces Procedural 3D Models)
-- Supports 360-degree spin frames, front, side, top, and lifestyle photos
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
);

-- Indexes for Fast Query Performance
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);
CREATE INDEX IF NOT EXISTS idx_product_metals_lookup ON product_metals(product_id, metal, in_stock);
CREATE INDEX IF NOT EXISTS idx_product_images_lookup ON product_images(product_id, metal, kind);

-- 5. Customer Orders
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    customer_phone TEXT,
    shipping_address TEXT,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'CONFIRMED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Order Line Items
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    metal TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 7. Wishlist
CREATE TABLE IF NOT EXISTS wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 8. Users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

-- 9. The Founder's Archival Designs ("The Sketchbook: from pencil to jewel")
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

CREATE INDEX IF NOT EXISTS idx_designs_product ON designs(product_id);
CREATE INDEX IF NOT EXISTS idx_designs_order ON designs(sort_order);

-- 10. Featured Edit Section (Faded Photo Band + 12-Column Editorial Grid)
CREATE TABLE IF NOT EXISTS feature_section (
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

CREATE TABLE IF NOT EXISTS feature_tiles (
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

CREATE INDEX IF NOT EXISTS idx_feature_section_active ON feature_section(active);
CREATE INDEX IF NOT EXISTS idx_feature_tiles_section ON feature_tiles(feature_section_id, sort_order);


