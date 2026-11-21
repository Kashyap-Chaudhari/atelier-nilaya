import os
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'atelier-nilaya-surat-luxury-secret-key-2026')

DB_PATH = os.path.join(os.path.dirname(__file__), 'nilaya.db')
STATIC_PRODUCTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'products')

@app.template_filter('format_inr')
def format_inr(value):
    if value is None or value == '':
        return ''
    try:
        val = int(round(float(value)))
    except (ValueError, TypeError):
        return str(value)
    
    s = str(val)
    if len(s) <= 3:
        return s
    last_three = s[-3:]
    other = s[:-3]
    parts = []
    while len(other) > 2:
        parts.insert(0, other[-2:])
        other = other[:-2]
    if other:
        parts.insert(0, other)
    return ','.join(parts) + ',' + last_three

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_cart_count():
    cart = session.get('cart', [])
    return sum(item.get('quantity', 1) for item in cart)

def get_wishlist_ids():
    user_id = session.get('user_id')
    if user_id:
        db = get_db()
        rows = db.execute('SELECT product_id FROM wishlist WHERE user_id = ?', (user_id,)).fetchall()
        return [r['product_id'] for r in rows]
    return session.get('guest_wishlist', [])

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    db = get_db()
    all_categories = db.execute('SELECT * FROM categories ORDER BY display_order ASC').fetchall()
    featured_products = db.execute("""
        SELECT p.*, c.name as category_name, c.slug as category_slug
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.is_featured = 1 OR p.tag IS NOT NULL
        LIMIT 8
    """).fetchall()

    # Query designs for "The Sketchbook: from pencil to jewel"
    design_rows = db.execute("""
        SELECT d.*, p.slug as product_slug, p.name as product_name, p.price as product_price,
               p.base_metal as product_base_metal, p.glb_file, COALESCE(p.spin_frames, 36) as spin_frames
        FROM designs d
        JOIN products p ON d.product_id = p.id
        ORDER BY d.sort_order ASC
    """).fetchall()

    designs = []
    for d in design_rows:
        d_dict = dict(d)
        pid = d_dict['product_id']

        # Check which metals have images for this product
        img_metals = db.execute("""
            SELECT DISTINCT metal FROM product_images
            WHERE product_id = ? AND kind IN ('spin', 'front')
        """, (pid,)).fetchall()
        available_metals = [m['metal'] for m in img_metals]
        if not available_metals:
            available_metals = ['yellow_gold', 'platinum', 'rose_gold']

        d_dict['metals'] = available_metals
        d_dict['default_metal'] = d_dict.get('product_base_metal') or (available_metals[0] if available_metals else 'yellow_gold')

        images_by_metal = {}
        for m in available_metals:
            frames = db.execute("""
                SELECT path, frame_index FROM product_images
                WHERE product_id = ? AND metal = ? AND kind = 'spin'
                ORDER BY frame_index ASC
            """, (pid, m)).fetchall()

            front_row = db.execute("""
                SELECT path FROM product_images
                WHERE product_id = ? AND metal = ? AND kind = 'front'
                LIMIT 1
            """, (pid, m)).fetchone()

            front_path = front_row['path'] if front_row else (frames[0]['path'] if frames else None)
            images_by_metal[m] = {
                'spin': [f['path'] for f in frames],
                'front': front_path
            }

        d_dict['images_by_metal'] = images_by_metal
        default_metal_data = images_by_metal.get(d_dict['default_metal'], {})
        d_dict['finished_photo'] = default_metal_data.get('front') or f"/static/products/{d_dict['product_slug']}/{d_dict['default_metal']}/front.webp"
        designs.append(d_dict)

    cart_count = get_cart_count()
    wishlist_ids = get_wishlist_ids()

    # Query Featured Edit Section & Tiles
    featured_edit = None
    f_sec = db.execute("SELECT * FROM feature_section WHERE active = 1 ORDER BY id ASC LIMIT 1").fetchone()
    if f_sec:
        featured_edit = dict(f_sec)
        f_tiles = db.execute("""
            SELECT * FROM feature_tiles 
            WHERE feature_section_id = ? AND active = 1 
            ORDER BY sort_order ASC
        """, (f_sec['id'],)).fetchall()
        
        tiles_list = []
        for t in f_tiles:
            t_dict = dict(t)
            if (t_dict.get('kind') == 'product_group' or t_dict.get('tile_type') == 'product_grid') and t_dict.get('product_ids'):
                p_ids = [int(x.strip()) for x in t_dict['product_ids'].split(',') if x.strip().isdigit()]
                if p_ids:
                    placeholders = ','.join(['?'] * len(p_ids))
                    prods_raw = db.execute(f"SELECT * FROM products WHERE id IN ({placeholders})", p_ids).fetchall()
                    prod_map = {p['id']: dict(p) for p in prods_raw}
                    ordered_prods = []
                    for pid in p_ids:
                        if pid in prod_map:
                            p_info = prod_map[pid]
                            m = p_info.get('metal', 'platinum').lower().replace(' ', '_').replace('18k_', '').replace('24k_', '')
                            if m not in ['platinum', 'rose_gold', 'yellow_gold', 'white_gold']:
                                m = 'platinum'
                            p_info['resolved_image'] = f"/static/products/{p_info['slug']}/{m}/front.webp"
                            ordered_prods.append(p_info)
                    t_dict['products'] = ordered_prods
            tiles_list.append(t_dict)
        featured_edit['tiles'] = tiles_list

    return render_template(
        'index.html',
        all_categories=all_categories,
        featured_products=featured_products,
        designs=designs,
        featured_edit=featured_edit,
        cart_count=cart_count,
        wishlist_ids=wishlist_ids
    )

@app.route('/c/<category_slug>')
def category(category_slug):
    db = get_db()
    cat = db.execute('SELECT * FROM categories WHERE slug = ?', (category_slug,)).fetchone()
    if not cat:
        return redirect(url_for('category', category_slug='rings'))

    all_categories = db.execute('SELECT * FROM categories ORDER BY display_order ASC').fetchall()

    # Query parameters for filters & sort
    metal_filter = request.args.get('metal', 'all').strip().lower()
    price_filter = request.args.get('price', 'all').strip().lower()
    stone_filter = request.args.get('stone', 'all').strip().lower()
    occasion_filter = request.args.get('occasion', 'all').strip().lower()
    sort_order = request.args.get('sort', 'featured').strip().lower()
    selected_metal_dot = request.args.get('metal_dot', '').strip().lower()

    # Base query for products in category
    query = """
        SELECT p.*, c.name as category_name, c.slug as category_slug
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE c.slug = ?
    """
    params = [category_slug]

    # Metal Filter
    if metal_filter and metal_filter != 'all':
        query += """
            AND p.id IN (
                SELECT product_id FROM product_metals 
                WHERE metal = ? AND in_stock = 1
            )
        """
        params.append(metal_filter)

    # Price Range Filter
    if price_filter == 'under_100k':
        query += " AND p.price < 100000"
    elif price_filter == '100k_250k':
        query += " AND p.price >= 100000 AND p.price <= 250000"
    elif price_filter == '250k_500k':
        query += " AND p.price > 250000 AND p.price <= 500000"
    elif price_filter == 'above_500k':
        query += " AND p.price > 500000"

    # Stone Type Filter
    if stone_filter and stone_filter != 'all':
        query += " AND (p.stone_type = ? OR p.stone LIKE ?)"
        params.extend([stone_filter, f'%{stone_filter}%'])

    # Occasion Filter
    if occasion_filter and occasion_filter != 'all':
        query += " AND p.occasion = ?"
        params.append(occasion_filter)

    # Sorting
    if sort_order == 'price_asc':
        query += " ORDER BY p.price ASC"
    elif sort_order == 'price_desc':
        query += " ORDER BY p.price DESC"
    elif sort_order == 'newest':
        query += " ORDER BY p.created_at DESC, p.id DESC"
    else: # featured
        query += " ORDER BY p.is_featured DESC, p.id ASC"

    product_rows = db.execute(query, params).fetchall()
    wishlist_ids = get_wishlist_ids()

    products = []
    for r in product_rows:
        p_dict = dict(r)
        
        # Attach product_metals table data
        metals_rows = db.execute(
            'SELECT metal, price, in_stock FROM product_metals WHERE product_id = ?', 
            (p_dict['id'],)
        ).fetchall()
        
        # Check which metals have images for this product (from product_images table or disk)
        img_metals = db.execute("""
            SELECT DISTINCT metal FROM product_images 
            WHERE product_id = ? AND kind IN ('spin', 'front')
        """, (p_dict['id'],)).fetchall()
        available_img_metals = set(row['metal'] for row in img_metals)
        if not available_img_metals:
            prod_dir = os.path.join(STATIC_PRODUCTS_DIR, p_dict['slug'])
            if os.path.exists(prod_dir):
                available_img_metals = set(d for d in os.listdir(prod_dir) if os.path.isdir(os.path.join(prod_dir, d)))

        metals_map = {}
        for m in metals_rows:
            metal_name = m['metal']
            has_img = metal_name in available_img_metals
            
            # Count 360 spin frames on disk for this metal
            spin_dir = os.path.join(STATIC_PRODUCTS_DIR, p_dict['slug'], metal_name, 'spin')
            frames_count = len([f for f in os.listdir(spin_dir) if f.endswith('.webp')]) if os.path.exists(spin_dir) else 0

            metals_map[metal_name] = {
                'price': m['price'],
                'in_stock': bool(m['in_stock']) and has_img,
                'has_images': has_img,
                'frames': frames_count
            }
        p_dict['metals'] = metals_map

        # Preselect the product's own listed metal (e.g. 18K White Gold -> platinum, never yellow)
        # If the category-wide metal filter is active, align to that filter if offered
        if metal_filter and metal_filter != 'all' and metals_map.get(metal_filter) and metals_map[metal_filter]['in_stock']:
            effective_metal = metal_filter
        else:
            effective_metal = p_dict['base_metal']
            if not metals_map.get(effective_metal) or not metals_map[effective_metal]['in_stock']:
                for m_key, m_val in metals_map.items():
                    if m_val['in_stock']:
                        effective_metal = m_key
                        break
        p_dict['effective_metal'] = effective_metal

        # Photographic Spin paths
        p_dict['spin_base'] = f"/static/products/{p_dict['slug']}/{effective_metal}/spin/"
        p_dict['spin_frames'] = metals_map.get(effective_metal, {}).get('frames', p_dict.get('spin_frames') or 36)
        p_dict['front_photo'] = f"/static/products/{p_dict['slug']}/{effective_metal}/front.webp"
        p_dict['lifestyle_photo'] = f"/static/products/{p_dict['slug']}/lifestyle-1.webp"

        # Calculate discount percentage if old_price exists from real values
        current_metal_price = metals_map.get(effective_metal, {}).get('price', p_dict['price'])
        p_dict['current_price'] = current_metal_price
        if p_dict.get('old_price') and p_dict['old_price'] > current_metal_price:
            discount_pct = round(((p_dict['old_price'] - current_metal_price) / p_dict['old_price']) * 100)
            p_dict['save_percent'] = discount_pct
        else:
            p_dict['save_percent'] = None

        p_dict['is_wishlisted'] = p_dict['id'] in wishlist_ids
        products.append(p_dict)

    # Active filters list for display chips
    active_filters = []
    if metal_filter != 'all':
        active_filters.append({'key': 'metal', 'label': f"Metal: {metal_filter.replace('_', ' ').title()}"})
    if price_filter != 'all':
        price_labels = {
            'under_100k': 'Under ₹1,00,000',
            '100k_250k': '₹1,00,000 – ₹2,50,000',
            '250k_500k': '₹2,50,000 – ₹5,00,000',
            'above_500k': 'Above ₹5,00,000'
        }
        active_filters.append({'key': 'price', 'label': f"Price: {price_labels.get(price_filter, price_filter)}"})
    if stone_filter != 'all':
        active_filters.append({'key': 'stone', 'label': f"Stone: {stone_filter.title()}"})
    if occasion_filter != 'all':
        active_filters.append({'key': 'occasion', 'label': f"Occasion: {occasion_filter.title()}"})

    return render_template(
        'category.html',
        category=cat,
        all_categories=all_categories,
        products=products,
        total_products=len(products),
        metal_filter=metal_filter,
        price_filter=price_filter,
        stone_filter=stone_filter,
        occasion_filter=occasion_filter,
        sort_order=sort_order,
        selected_metal_dot=selected_metal_dot,
        active_filters=active_filters,
        bag_count=get_cart_count(),
        wishlist_count=len(wishlist_ids)
    )

# Product detail supporting both /p/<slug> and /p/<int:product_id>
@app.route('/p/<slug_or_id>')
def product_detail(slug_or_id):
    db = get_db()
    
    if str(slug_or_id).isdigit():
        product = db.execute("""
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        """, (int(slug_or_id),)).fetchone()
    else:
        product = db.execute("""
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.slug = ?
        """, (slug_or_id,)).fetchone()

    if not product:
        return redirect(url_for('category', category_slug='rings'))

    product_id = product['id']
    slug = product['slug']

    metals_rows = db.execute(
        'SELECT metal, price, in_stock FROM product_metals WHERE product_id = ?', 
        (product_id,)
    ).fetchall()

    metals = {r['metal']: {'price': r['price'], 'in_stock': bool(r['in_stock'])} for r in metals_rows}

    # Selected metal from query or base_metal
    selected_metal = request.args.get('metal', product['base_metal']).strip().lower()
    if selected_metal not in metals or not metals[selected_metal]['in_stock']:
        for m, info in metals.items():
            if info['in_stock']:
                selected_metal = m
                break

    current_price = metals.get(selected_metal, {}).get('price', product['price'])
    old_price = product['old_price']
    save_percent = None
    if old_price and old_price > current_price:
        save_percent = round(((old_price - current_price) / old_price) * 100)

    # Fetch product photographic image structure from product_images table
    images_rows = db.execute("""
        SELECT metal, kind, frame_index, path, alt
        FROM product_images
        WHERE product_id = ?
        ORDER BY kind, frame_index ASC
    """, (product_id,)).fetchall()

    images_by_metal = {}
    lifestyle_img = f"/static/products/{slug}/lifestyle-1.webp"

    for r in images_rows:
        m = r['metal']
        k = r['kind']
        if k == 'lifestyle':
            lifestyle_img = r['path']
            continue
        if m not in images_by_metal:
            images_by_metal[m] = {
                'front': f"/static/products/{slug}/{m}/front.webp",
                'side': f"/static/products/{slug}/{m}/side.webp",
                'top': f"/static/products/{slug}/{m}/top.webp",
                'spin_base': f"/static/products/{slug}/{m}/spin/"
            }
        if k in ('front', 'side', 'top'):
            images_by_metal[m][k] = r['path']

    all_categories = db.execute('SELECT * FROM categories ORDER BY display_order ASC').fetchall()
    wishlist_ids = get_wishlist_ids()

    return render_template(
        'product.html',
        product=product,
        metals=metals,
        selected_metal=selected_metal,
        current_price=current_price,
        save_percent=save_percent,
        images_by_metal=images_by_metal,
        lifestyle_img=lifestyle_img,
        all_categories=all_categories,
        is_wishlisted=product['id'] in wishlist_ids,
        bag_count=get_cart_count(),
        wishlist_count=len(wishlist_ids)
    )

# Required API: /api/products/<slug>/images returns image structure
@app.route('/api/products/<slug>/images')
def api_product_images(slug):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE slug = ?", (slug,)).fetchone()
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    images_rows = db.execute("""
        SELECT metal, kind, frame_index, path, alt
        FROM product_images
        WHERE product_id = ?
        ORDER BY kind, frame_index ASC
    """, (product['id'],)).fetchall()

    metals_dict = {}
    lifestyle_info = {
        'path': f"/static/products/{slug}/lifestyle-1.webp",
        'alt': f"{product['name']} luxury lifestyle view"
    }

    for row in images_rows:
        metal = row['metal']
        kind = row['kind']
        path = row['path']
        alt = row['alt']

        if kind == 'lifestyle':
            lifestyle_info = {'path': path, 'alt': alt}
            continue

        if metal not in metals_dict:
            metals_dict[metal] = {
                'spin_base': f"/static/products/{slug}/{metal}/spin/",
                'frames': [],
                'front': None,
                'side': None,
                'top': None
            }

        if kind == 'spin':
            metals_dict[metal]['frames'].append(path)
        elif kind in ('front', 'side', 'top'):
            metals_dict[metal][kind] = path

    return jsonify({
        'id': product['id'],
        'name': product['name'],
        'slug': product['slug'],
        'base_metal': product['base_metal'],
        'spin_frames': product['spin_frames'] or 36,
        'lifestyle': lifestyle_info,
        'metals': metals_dict
    })

@app.route('/wishlist')
def wishlist():
    db = get_db()
    user_id = session.get('user_id')
    all_categories = db.execute('SELECT * FROM categories ORDER BY display_order ASC').fetchall()
    
    param_ids = request.args.get('ids', '').strip()
    guest_ids = [int(x) for x in param_ids.split(',') if x.isdigit()] if param_ids else []
    
    if user_id:
        query = """
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE w.user_id = ?
            ORDER BY w.created_at DESC
        """
        rows = db.execute(query, (user_id,)).fetchall()
    elif guest_ids:
        placeholders = ','.join('?' for _ in guest_ids)
        query = f"""
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id IN ({placeholders})
        """
        rows = db.execute(query, guest_ids).fetchall()
    else:
        rows = []

    products = []
    for r in rows:
        p_dict = dict(r)
        metals_rows = db.execute('SELECT metal, price, in_stock FROM product_metals WHERE product_id = ?', (p_dict['id'],)).fetchall()
        p_dict['metals'] = {m['metal']: {'price': m['price'], 'in_stock': bool(m['in_stock'])} for m in metals_rows}
        p_dict['is_wishlisted'] = True
        if p_dict.get('old_price') and p_dict['old_price'] > p_dict['price']:
            p_dict['save_percent'] = round(((p_dict['old_price'] - p_dict['price']) / p_dict['old_price']) * 100)
        else:
            p_dict['save_percent'] = None
        products.append(p_dict)

    return render_template(
        'wishlist.html',
        products=products,
        all_categories=all_categories,
        bag_count=get_cart_count(),
        wishlist_count=len(products)
    )

@app.route('/api/wishlist/toggle', methods=['POST'])
def api_wishlist_toggle():
    data = request.get_json(silent=True) or request.form
    try:
        product_id = int(data.get('product_id', 0))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Invalid product ID'}), 400

    user_id = session.get('user_id')
    db = get_db()
    
    if user_id:
        existing = db.execute('SELECT id FROM wishlist WHERE user_id = ? AND product_id = ?', (user_id, product_id)).fetchone()
        if existing:
            db.execute('DELETE FROM wishlist WHERE user_id = ? AND product_id = ?', (user_id, product_id))
            db.commit()
            is_wishlisted = False
        else:
            db.execute('INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)', (user_id, product_id))
            db.commit()
            is_wishlisted = True
        count = db.execute('SELECT COUNT(*) as cnt FROM wishlist WHERE user_id = ?', (user_id,)).fetchone()['cnt']
    else:
        wishlist_list = session.get('guest_wishlist', [])
        if product_id in wishlist_list:
            wishlist_list.remove(product_id)
            is_wishlisted = False
        else:
            wishlist_list.append(product_id)
            is_wishlisted = True
        session['guest_wishlist'] = wishlist_list
        session.modified = True
        count = len(wishlist_list)

    return jsonify({'success': True, 'is_wishlisted': is_wishlisted, 'count': count})

@app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
def api_cart():
    if 'cart' not in session:
        session['cart'] = []

    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        try:
            product_id = int(data.get('product_id', 0))
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'Invalid product ID'}), 400

        metal = data.get('metal', 'yellow_gold').strip().lower().replace('-', '_')
        quantity = int(data.get('quantity', 1))

        db = get_db()
        product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if not product:
            return jsonify({'success': False, 'error': 'Product not found. Please refresh the page and try again.'}), 404

        metal_info = db.execute(
            'SELECT price, in_stock FROM product_metals WHERE product_id = ? AND metal = ?',
            (product_id, metal)
        ).fetchone()

        if not metal_info or not metal_info['in_stock']:
            metal_label = metal.replace('_', ' ').title()
            return jsonify({
                'success': False, 
                'error': f'The selected metal ({metal_label}) is currently unavailable for this piece. Please choose an available metal.'
            }), 400

        price = metal_info['price']

        found = False
        for item in session['cart']:
            if item['product_id'] == product_id and item['metal'] == metal:
                item['quantity'] += quantity
                found = True
                break
        if not found:
            session['cart'].append({
                'product_id': product_id,
                'name': product['name'],
                'metal': metal,
                'price': price,
                'quantity': quantity,
                'purity': product['purity'],
                'image': f"/static/products/{product['slug']}/{metal}/front.webp"
            })

        session.modified = True
        return jsonify({
            'success': True,
            'count': get_cart_count(),
            'message': 'Added to your bag'
        })

    elif request.method == 'DELETE':
        data = request.get_json(silent=True) or request.form
        try:
            product_id = int(data.get('product_id', 0))
            metal = data.get('metal', '').strip().lower()
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'Invalid product'}), 400

        session['cart'] = [item for item in session.get('cart', []) if not (item['product_id'] == product_id and item['metal'] == metal)]
        session.modified = True
        return jsonify({'success': True, 'count': get_cart_count()})

    # GET
    cart_items = session.get('cart', [])
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    return jsonify({
        'items': cart_items,
        'count': get_cart_count(),
        'total': total_amount
    })

@app.route('/bag')
def bag():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    db = get_db()
    all_categories = db.execute('SELECT * FROM categories ORDER BY display_order ASC').fetchall()
    return render_template(
        'bag.html',
        cart=cart,
        total=total,
        all_categories=all_categories,
        bag_count=get_cart_count(),
        wishlist_count=len(get_wishlist_ids())
    )

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('category', category_slug='rings'))

    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        
        customer_name = request.form.get('customer_name', 'Private Client')
        customer_email = request.form.get('customer_email', 'client@ateliernilaya.com')
        customer_phone = request.form.get('customer_phone', '+91 98250 00000')
        shipping_address = request.form.get('shipping_address', 'Surat, Gujarat, India')
        total_amount = sum(item['price'] * item['quantity'] for item in cart)

        cur.execute("""
            INSERT INTO orders (customer_name, customer_email, customer_phone, shipping_address, total_amount)
            VALUES (?, ?, ?, ?, ?)
        """, (customer_name, customer_email, customer_phone, shipping_address, total_amount))
        
        order_id = cur.lastrowid

        for item in cart:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, metal, price, quantity)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, item['product_id'], item['metal'], item['price'], item['quantity']))

        db.commit()
        session['cart'] = []
        session.modified = True

        return render_template('order_confirmed.html', order_id=order_id, total=total_amount, bag_count=0)

    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('checkout.html', cart=cart, total=total, bag_count=get_cart_count())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
