import sqlite3
import os
import hashlib

DB_PATH = 'nilaya.db'

def run_migrations():
    print(f"Connecting to {DB_PATH} for Admin migrations...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Staff Users
    c.execute("""
    CREATE TABLE IF NOT EXISTS staff_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'manager', -- 'owner', 'manager', 'stock_staff', 'delivery_staff'
        phone TEXT,
        two_factor_enabled INTEGER DEFAULT 0,
        two_factor_secret TEXT,
        is_active INTEGER DEFAULT 1,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Activity Logs
    c.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_name TEXT NOT NULL,
        user_role TEXT NOT NULL,
        action TEXT NOT NULL,
        module TEXT NOT NULL,
        entity_type TEXT,
        entity_id INTEGER,
        details TEXT,
        old_value TEXT,
        new_value TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Gold Rates & History
    c.execute("""
    CREATE TABLE IF NOT EXISTS gold_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rate_24k REAL NOT NULL, -- per gram in INR
        rate_22k REAL NOT NULL,
        rate_18k REAL NOT NULL,
        rate_silver REAL NOT NULL,
        effective_date TEXT NOT NULL,
        updated_by TEXT NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Stock Adjustments Log
    c.execute("""
    CREATE TABLE IF NOT EXISTS stock_adjustments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        change_qty INTEGER NOT NULL,
        new_qty INTEGER NOT NULL,
        reason TEXT NOT NULL,
        staff_id INTEGER,
        staff_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
    );
    """)

    # 5. Custom Requests & Bespoke Commissions
    c.execute("""
    CREATE TABLE IF NOT EXISTS custom_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        client_phone TEXT NOT NULL,
        client_email TEXT,
        piece_type TEXT NOT NULL,
        reference_photo TEXT,
        description TEXT NOT NULL,
        budget_range TEXT,
        quoted_price REAL DEFAULT 0,
        advance_paid REAL DEFAULT 0,
        balance_due REAL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'new', -- 'new', 'quoted', 'in_making', 'ready', 'delivered', 'cancelled'
        karigar_notes TEXT,
        target_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Customer Profiles & Family Lineage
    c.execute("""
    CREATE TABLE IF NOT EXISTS customer_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        email TEXT,
        city TEXT,
        address TEXT,
        family_occasions TEXT, -- JSON or bullet points of milestones
        notes TEXT,
        is_vip INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Store Settings
    c.execute("""
    CREATE TABLE IF NOT EXISTS store_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 8. Website Content Versions
    c.execute("""
    CREATE TABLE IF NOT EXISTS website_content_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_key TEXT NOT NULL, -- 'announcement_bar', 'heritage_section', 'faq', 'customer_stories'
        content_json TEXT NOT NULL,
        version_number INTEGER NOT NULL,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 9. Customer Stories / Reviews for Homepage
    c.execute("""
    CREATE TABLE IF NOT EXISTS customer_stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        occasion TEXT NOT NULL,
        quote TEXT NOT NULL,
        client_name TEXT NOT NULL,
        city TEXT NOT NULL,
        piece_name TEXT NOT NULL,
        year INTEGER NOT NULL,
        photo_path TEXT,
        is_approved INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 10. FAQ Items
    c.execute("""
    CREATE TABLE IF NOT EXISTS faq_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Check and add columns to products table if missing
    c.execute("PRAGMA table_info(products);")
    prod_cols = [row[1] for row in c.fetchall()]
    
    new_prod_cols = [
        ("is_deleted", "INTEGER DEFAULT 0"),
        ("stock_qty", "INTEGER DEFAULT 1"),
        ("low_stock_threshold", "INTEGER DEFAULT 1"),
        ("stock_status", "TEXT DEFAULT 'Available'"), # 'Available', 'Reserved', 'Sold', 'Made-to-order'
        ("making_charge_type", "TEXT DEFAULT 'percent'"), # 'percent', 'fixed'
        ("making_charge_value", "REAL DEFAULT 12.0"),
        ("gold_weight_grams", "REAL DEFAULT 14.5"),
        ("stone_value", "REAL DEFAULT 25000.0"),
        ("huid_number", "TEXT DEFAULT 'HUID-916-SURAT'"),
        ("certificate_file", "TEXT"),
        ("collection_name", "TEXT DEFAULT 'Archival Heritage'")
    ]
    for col_name, col_def in new_prod_cols:
        if col_name not in prod_cols:
            c.execute(f"ALTER TABLE products ADD COLUMN {col_name} {col_def};")
            print(f"Added column {col_name} to products")

    # Check and add columns to orders table if missing
    c.execute("PRAGMA table_info(orders);")
    order_cols = [row[1] for row in c.fetchall()]
    
    new_order_cols = [
        ("courier_name", "TEXT DEFAULT 'Sequel Logistics'"),
        ("tracking_number", "TEXT"),
        ("insured_value", "REAL DEFAULT 0"),
        ("dispatch_date", "TEXT"),
        ("delivery_status", "TEXT DEFAULT 'Processing'"),
        ("bench_notes", "TEXT")
    ]
    for col_name, col_def in new_order_cols:
        if col_name not in order_cols:
            c.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_def};")
            print(f"Added column {col_name} to orders")

    # Seed Default Staff Users if not present
    c.execute("SELECT count(*) FROM staff_users;")
    if c.fetchone()[0] == 0:
        # Default Owner: owner@ateliernilaya.com / NilayaOwner1954!
        # Manager: manager@ateliernilaya.com / NilayaManager1954!
        # Stock: stock@ateliernilaya.com / NilayaStock1954!
        # Delivery: delivery@ateliernilaya.com / NilayaDelivery1954!
        def h(pwd):
            return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

        staff_seed = [
            ("owner@ateliernilaya.com", "Jayantilal Choksi (Owner)", h("NilayaOwner1954!"), "owner", "+91 98250 11954", 1, "729401"),
            ("manager@ateliernilaya.com", "Devang Choksi (Atelier Manager)", h("NilayaManager1954!"), "manager", "+91 98250 22954", 0, None),
            ("stock@ateliernilaya.com", "Ramesh Karigar (Stock Head)", h("NilayaStock1954!"), "stock_staff", "+91 98250 33954", 0, None),
            ("delivery@ateliernilaya.com", "Vikram Patel (Dispatch Coordinator)", h("NilayaDelivery1954!"), "delivery_staff", "+91 98250 44954", 0, None)
        ]
        c.executemany("""
            INSERT INTO staff_users (email, name, password_hash, role, phone, two_factor_enabled, two_factor_secret)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, staff_seed)
        print("Seeded 4 default staff accounts (Owner, Manager, Stock Staff, Delivery Staff)")

    # Seed Current Gold Rate if empty
    c.execute("SELECT count(*) FROM gold_rates;")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO gold_rates (rate_24k, rate_22k, rate_18k, rate_silver, effective_date, updated_by, notes)
            VALUES (7850.0, 7200.0, 5890.0, 92.0, date('now'), 'Jayantilal Choksi (Owner)', 'Official Surat Zaveri Bazaar Bench Benchmark')
        """)
        print("Seeded initial live gold rate: 22K = ₹7,200/g, 24K = ₹7,850/g")

    # Seed Default Store Settings if empty
    default_settings = [
        ("business_name", "Atelier Nilaya Haute Joaillerie"),
        ("founded_year", "1954"),
        ("showroom_address", "Atelier Nilaya, Nanpura Main Road, Surat, Gujarat 395001"),
        ("contact_phone", "+91 98250 11954"),
        ("contact_email", "concierge@ateliernilaya.com"),
        ("gst_number", "[add GST number]"),
        ("courier_partners", "[add Courier partners: Sequel Logistics, BVC Logistics]"),
        ("payment_gateway", "[add Payment gateway: Razorpay Live / Bank Wire]"),
        ("whatsapp_number", "[add WhatsApp number: +91 98250 11954]"),
        ("brand_serif_font", "Cormorant Garamond"),
        ("announcement_bar_text", "Complimentary Armored Courier Transit Across India • Private Viewing Available at Surat Atelier"),
        ("announcement_bar_link", "#visit")
    ]
    for key, val in default_settings:
        c.execute("INSERT OR IGNORE INTO store_settings (setting_key, setting_value) VALUES (?, ?);", (key, val))

    # Seed FAQ Items if empty
    c.execute("SELECT count(*) FROM faq_items;")
    if c.fetchone()[0] == 0:
        faqs = [
            ("BIS hallmark and stone certification", "Every piece is stamped with the official government BIS 916 (22K) or 750 (18K) hallmark alongside our private atelier maker's mark. All solitaires carry independent laboratory certificates. [add answers]", 1),
            ("Customisation and timeline", "Bespoke commissions begin at the bench with archival pencil renderings. Handcrafting, stone calibration, casting, and hallmarking take 3 to 4 weeks. [add answers]", 2),
            ("Exchange and buyback", "Lifetime exchange and buyback guarantee: 100% metal value and 90% diamond value against exchange, or 95% metal and 80% diamond against direct repurchase. [add answers]", 3),
            ("Insured delivery across India", "Every order is 100% transit-insured from our Surat vault to your hands via armored couriers (Sequel and BVC). OTP verification required at doorstep. [add answers]", 4),
            ("Making-charge breakup on the bill", "Yes. Invoices clearly separate net gold weight, stone weight, live gold rate, and craftsmanship charges. No opaque compound markups. [add answers]", 5),
            ("Care for polki and kundan", "Polki diamonds and ancestral kundan settings are laid upon pure 24k gold foil and must never be submerged in water or perfumes. Clean with dry microfibre cloth. [add answers]", 6),
            ("Seeing a piece in person before buying", "Connoisseurs are warmly welcomed to reserve a private viewing at our Surat Atelier, or schedule a secure video consultation with our head master karigar. [add answers]", 7)
        ]
        c.executemany("INSERT INTO faq_items (question, answer, sort_order) VALUES (?, ?, ?);", faqs)
        print("Seeded 7 FAQ items")

    # Seed Customer Stories if empty
    c.execute("SELECT count(*) FROM customer_stories;")
    if c.fetchone()[0] == 0:
        stories = [
            ("Her wedding morning", "When my grandmother fastened the choker, she whispered that three generations of Surat craftsmanship were holding me today. I never took it off until dawn.", "Meera", "Ahmedabad", "Polki choker necklace", 2025, "/static/lifestyle/lifestyle-product-1.webp", 1),
            ("A first grandchild", "We wanted an heirloom that will outlive us both. Holding the baby while wearing my mother's emerald ring brought tears to the whole room.", "Devika", "Surat", "Emerald solitaire ring", 2024, "/static/lifestyle/lifestyle-product-10.webp", 2),
            ("Our 25th anniversary", "A quarter century together marked with unheated pink sapphires. The weight of 24k gold feels intimate, grounding, and eternal.", "Radhika & Alok", "Mumbai", "Pink sapphire signet band", 2025, "/static/lifestyle/lifestyle-product-2.webp", 3),
            ("The heirloom handover", "Handing my daughter her first uncut diamond piece from Nilaya felt like passing on our family's courage, grace, and blessings.", "Pooja", "Vadodara", "Syndicate polki bracelet", 2026, "/static/lifestyle/lifestyle-product-14.webp", 4)
        ]
        c.executemany("INSERT INTO customer_stories (occasion, quote, client_name, city, piece_name, year, photo_path, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", stories)
        print("Seeded 4 customer stories")

    # Seed Customer Profiles from existing orders
    c.execute("SELECT DISTINCT customer_name, customer_email, customer_phone, shipping_address FROM orders;")
    for row in c.fetchall():
        name, email, phone, addr = row[0], row[1], row[2], row[3]
        if phone:
            c.execute("""
                INSERT OR IGNORE INTO customer_profiles (name, phone, email, address, is_vip)
                VALUES (?, ?, ?, ?, 1);
            """, (name, phone, email, addr))

    conn.commit()
    conn.close()
    print("Database migrations for Admin Panel completed successfully!")

if __name__ == '__main__':
    run_migrations()
