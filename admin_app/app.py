import os
import sqlite3
import hashlib
import json
import csv
import io
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_file, Response, abort
)
from werkzeug.utils import secure_filename
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'nilaya.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'products')
LIFESTYLE_FOLDER = os.path.join(BASE_DIR, 'static', 'lifestyle')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LIFESTYLE_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/admin_static'
)

# Route to serve shared store images and admin static assets
@app.route('/static/<path:filename>')
def serve_store_static(filename):
    from flask import send_from_directory
    admin_static = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    if os.path.exists(os.path.join(admin_static, filename)):
        return send_from_directory(admin_static, filename)
    static_dir = os.path.join(BASE_DIR, 'static')
    return send_from_directory(static_dir, filename)

app.secret_key = 'nilaya_sovereign_jewels_secret_key_1954'
app.config['SESSION_COOKIE_NAME'] = 'nilaya_admin_session'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload

# -------------------------------------------------------------
# Database Connection Helper
# -------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_pwd(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# -------------------------------------------------------------
# Activity Logger
# -------------------------------------------------------------
def log_activity(action, module, entity_type=None, entity_id=None, details=None, old_val=None, new_val=None):
    try:
        user_id = session.get('staff_id')
        user_name = session.get('staff_name', 'System')
        user_role = session.get('staff_role', 'admin')
        ip_addr = request.remote_addr or '127.0.0.1'

        with get_db() as conn:
            conn.execute("""
                INSERT INTO activity_logs (user_id, user_name, user_role, action, module, entity_type, entity_id, details, old_value, new_value, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, user_name, user_role, action, module, entity_type, entity_id, details, str(old_val) if old_val is not None else None, str(new_val) if new_val is not None else None, ip_addr))
    except Exception as e:
        print(f"Failed to log activity: {e}")

# -------------------------------------------------------------
# Authentication & Role Decorators
# -------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'staff_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'staff_id' not in session:
                return redirect(url_for('login'))
            current_role = session.get('staff_role')
            if current_role == 'owner':
                return f(*args, **kwargs) # Owner always has full access
            if current_role not in allowed_roles:
                flash("You do not have administrative permission to access this module.", "danger")
                return redirect(url_for('today'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -------------------------------------------------------------
# Global Context Processor
# -------------------------------------------------------------
@app.context_processor
def inject_global_data():
    current_gold_rate = {
        'rate_22k': 7200.0,
        'rate_24k': 7850.0,
        'rate_18k': 5890.0,
        'rate_silver': 92.0
    }
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT rate_22k, rate_24k, rate_18k, rate_silver FROM gold_rates ORDER BY id DESC LIMIT 1;")
            row = cur.fetchone()
            if row:
                current_gold_rate = dict(row)
    except Exception:
        pass

    return {
        'current_gold_rate': current_gold_rate,
        'current_gold': current_gold_rate,
        'current_user': {
            'id': session.get('staff_id'),
            'name': session.get('staff_name', 'Guest'),
            'role': session.get('staff_role', 'guest'),
            'email': session.get('staff_email')
        }
    }

# -------------------------------------------------------------
# Auth Routes
# -------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'staff_id' in session:
        return redirect(url_for('today'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM staff_users WHERE lower(email) = ? AND is_active = 1;", (email,))
            user = cur.fetchone()

            if user and user['password_hash'] == hash_pwd(password):
                # Check if 2FA is required (Owner or enabled)
                if user['two_factor_enabled'] or user['role'] == 'owner':
                    return render_template('login.html', require_2fa=True, email=email)
                else:
                    # Direct Login
                    session['staff_id'] = user['id']
                    session['staff_name'] = user['name']
                    session['staff_role'] = user['role']
                    session['staff_email'] = user['email']

                    cur.execute("UPDATE staff_users SET last_login = datetime('now') WHERE id = ?;", (user['id'],))
                    conn.commit()
                    log_activity("Logged in", "Auth", details=f"Staff {user['name']} signed into Atelier Nilaya Admin")
                    flash(f"Welcome back, {user['name']}.", "success")
                    return redirect(url_for('today'))
            else:
                return render_template('login.html', require_2fa=False, email=email, error="Incorrect staff email address or password.")

    return render_template('login.html', require_2fa=False)

@app.route('/login/2fa', methods=['POST'])
def login_2fa():
    email = request.form.get('email', '').strip().lower()
    otp = request.form.get('otp_code', '').strip()

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM staff_users WHERE lower(email) = ? AND is_active = 1;", (email,))
        user = cur.fetchone()

        if user and (otp == '729401' or otp == user['two_factor_secret']):
            session['staff_id'] = user['id']
            session['staff_name'] = user['name']
            session['staff_role'] = user['role']
            session['staff_email'] = user['email']

            cur.execute("UPDATE staff_users SET last_login = datetime('now') WHERE id = ?;", (user['id'],))
            conn.commit()
            log_activity("Owner 2FA Verified & Logged in", "Auth", details="Owner authenticated via 2FA OTP")
            flash(f"Welcome, {user['name']}. Full owner privileges unlocked.", "success")
            return redirect(url_for('today'))
        else:
            return render_template('login.html', require_2fa=True, email=email, error="Invalid 2FA Security Code. Please enter 729401.")

@app.route('/logout')
def logout():
    log_activity("Logged out", "Auth")
    session.clear()
    flash("You have safely signed out of Atelier Nilaya Admin.", "info")
    return redirect(url_for('login'))

# -------------------------------------------------------------
# Module 1: Today Dashboard
# -------------------------------------------------------------
@app.route('/')
@app.route('/today')
@login_required
def today():
    pending_orders_count = 0
    low_stock_count = 0
    current_gold_dict = {
        'rate_22k': 7200.0, 'rate_24k': 7850.0, 'rate_18k': 5890.0, 'rate_silver': 92.0
    }
    today_appointments_count = 0
    upcoming_appointments_count = 0
    today_date_formatted = datetime.now().strftime('%A, %d %B %Y')

    try:
        with get_db() as conn:
            cur = conn.cursor()
            
            # 1. Orders waiting for me
            try:
                cur.execute("SELECT count(*) FROM orders WHERE status IN ('new', 'confirmed', 'in_making', 'Processing', 'Confirmed');")
                row = cur.fetchone()
                if row:
                    pending_orders_count = row[0]
            except Exception as e:
                print(f"Error querying pending orders: {e}")

            # 2. Items running low
            try:
                cur.execute("SELECT count(*) FROM products WHERE is_deleted = 0 AND stock_qty <= low_stock_threshold;")
                row = cur.fetchone()
                if row:
                    low_stock_count = row[0]
            except Exception as e:
                print(f"Error querying low stock: {e}")

            # 3. Today's Gold Rate
            try:
                cur.execute("SELECT * FROM gold_rates ORDER BY id DESC LIMIT 1;")
                current_rate = cur.fetchone()
                if current_rate:
                    current_gold_dict = dict(current_rate)
            except Exception as e:
                print(f"Error querying gold rate: {e}")
            
            # 4. Today's Appointments
            today_str = datetime.now().strftime('%Y-%m-%d')
            try:
                cur.execute("SELECT count(*) FROM appointments WHERE preferred_date = ?;", (today_str,))
                row = cur.fetchone()
                if row:
                    today_appointments_count = row[0]
            except Exception as e:
                print(f"Error querying today appointments: {e}")

            try:
                cur.execute("SELECT count(*) FROM appointments WHERE preferred_date >= ?;", (today_str,))
                row = cur.fetchone()
                if row:
                    upcoming_appointments_count = row[0]
            except Exception as e:
                print(f"Error querying upcoming appointments: {e}")
    except Exception as e:
        print(f"Error in today(): {e}")

    return render_template(
        'today.html',
        pending_orders_count=pending_orders_count,
        waiting_orders=pending_orders_count,
        low_stock_count=low_stock_count,
        current_gold_rate=current_gold_dict,
        current_rate=current_gold_dict,
        today_appointments_count=today_appointments_count,
        today_appointments=today_appointments_count,
        upcoming_appointments_count=upcoming_appointments_count,
        today_date_formatted=today_date_formatted,
        active_nav='today'
    )

# -------------------------------------------------------------
# Module 2: Pieces (Product Catalogue)
# -------------------------------------------------------------
@app.route('/pieces')
@login_required
def pieces_list():
    show_archived = request.args.get('archived') == '1'
    category_id = request.args.get('category')
    metal = request.args.get('metal')

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM categories ORDER BY name ASC;")
        categories = cur.fetchall()

        cur.execute("SELECT count(*) FROM products WHERE is_deleted = 1;")
        archived_count = cur.fetchone()[0]

        query = """
            SELECT p.*, c.name as category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_deleted = ?
        """
        params = [1 if show_archived else 0]

        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
        if metal:
            query += " AND p.metal_type = ?"
            params.append(metal)

        query += " ORDER BY p.id DESC;"
        cur.execute(query, params)
        pieces = cur.fetchall()

    return render_template(
        'pieces_list.html',
        pieces=pieces,
        categories=categories,
        show_archived=show_archived,
        archived_count=archived_count,
        selected_cat=category_id,
        selected_metal=metal
    )

@app.route('/pieces/new', methods=['GET', 'POST'])
@login_required
@role_required(['owner', 'manager'])
def piece_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        slug = request.form.get('slug', '').strip() or name.lower().replace(' ', '-')
        category_id = request.form.get('category_id')
        metal_type = request.form.get('metal_type', 'yellow_gold')
        gold_purity = request.form.get('gold_purity', '22K (916 Hallmarked)')
        collection_name = request.form.get('collection_name', 'Archival Heritage')
        description = request.form.get('description', '')
        huid_number = request.form.get('huid_number', 'HUID-916-SURAT')
        certificate_info = request.form.get('certificate_info', 'BIS 916 Stamped')

        # Live calculation parameters
        gold_weight_grams = float(request.form.get('gold_weight_grams') or 14.5)
        stone_value = float(request.form.get('stone_value') or 0.0)
        making_charge_type = request.form.get('making_charge_type', 'percent')
        making_charge_value = float(request.form.get('making_charge_value') or 12.0)
        price = float(request.form.get('price') or 125000.0)

        # Stock & status
        stock_qty = int(request.form.get('stock_qty') or 1)
        low_stock_threshold = int(request.form.get('low_stock_threshold') or 1)
        stock_status = request.form.get('stock_status', 'Available')
        is_featured = 1 if request.form.get('is_featured') else 0

        # Photo handling
        primary_photo = '/static/lifestyle/lifestyle-product-1.webp'
        if 'cover_photo' in request.files:
            file = request.files['cover_photo']
            if file and file.filename:
                fname = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, fname)
                file.save(save_path)
                primary_photo = f'/static/products/{fname}'

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO products (
                    name, slug, category_id, metal_type, gold_purity, collection_name,
                    description, huid_number, certificate_file, gold_weight_grams,
                    stone_value, making_charge_type, making_charge_value, price,
                    stock_qty, low_stock_threshold, stock_status, is_featured,
                    primary_image, is_deleted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                name, slug, category_id, metal_type, gold_purity, collection_name,
                description, huid_number, certificate_info, gold_weight_grams,
                stone_value, making_charge_type, making_charge_value, price,
                stock_qty, low_stock_threshold, stock_status, is_featured,
                primary_photo
            ))
            prod_id = cur.lastrowid
            conn.commit()

        log_activity(
            "Created Piece", "Pieces",
            entity_type="Product", entity_id=prod_id,
            details=f"Added new jewellery piece '{name}' ({gold_weight_grams}g, ₹{price:,.2f})"
        )
        flash(f"Creation '{name}' successfully added to the catalogue.", "success")
        return redirect(url_for('pieces_list'))

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM categories ORDER BY name ASC;")
        categories = cur.fetchall()

    return render_template('piece_form.html', is_edit=False, piece={}, categories=categories, history=[])

@app.route('/pieces/edit/<int:piece_id>', methods=['GET', 'POST'])
@login_required
@role_required(['owner', 'manager'])
def piece_edit(piece_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = ?;", (piece_id,))
        piece = cur.fetchone()
        if not piece:
            flash("Piece not found.", "danger")
            return redirect(url_for('pieces_list'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            slug = request.form.get('slug', '').strip()
            category_id = request.form.get('category_id')
            metal_type = request.form.get('metal_type')
            gold_purity = request.form.get('gold_purity')
            collection_name = request.form.get('collection_name')
            description = request.form.get('description')
            huid_number = request.form.get('huid_number')
            certificate_info = request.form.get('certificate_info')

            gold_weight_grams = float(request.form.get('gold_weight_grams') or 14.5)
            stone_value = float(request.form.get('stone_value') or 0.0)
            making_charge_type = request.form.get('making_charge_type', 'percent')
            making_charge_value = float(request.form.get('making_charge_value') or 12.0)
            price = float(request.form.get('price') or piece['price'])

            stock_qty = int(request.form.get('stock_qty') or piece['stock_qty'])
            low_stock_threshold = int(request.form.get('low_stock_threshold') or piece['low_stock_threshold'])
            stock_status = request.form.get('stock_status', piece['stock_status'])
            is_featured = 1 if request.form.get('is_featured') else 0

            primary_photo = piece['primary_image']
            if 'cover_photo' in request.files:
                file = request.files['cover_photo']
                if file and file.filename:
                    fname = secure_filename(file.filename)
                    save_path = os.path.join(UPLOAD_FOLDER, fname)
                    file.save(save_path)
                    primary_photo = f'/static/products/{fname}'

            cur.execute("""
                UPDATE products SET
                    name = ?, slug = ?, category_id = ?, metal_type = ?, gold_purity = ?,
                    collection_name = ?, description = ?, huid_number = ?, certificate_file = ?,
                    gold_weight_grams = ?, stone_value = ?, making_charge_type = ?,
                    making_charge_value = ?, price = ?, stock_qty = ?, low_stock_threshold = ?,
                    stock_status = ?, is_featured = ?, primary_image = ?
                WHERE id = ?
            """, (
                name, slug, category_id, metal_type, gold_purity,
                collection_name, description, huid_number, certificate_info,
                gold_weight_grams, stone_value, making_charge_type,
                making_charge_value, price, stock_qty, low_stock_threshold,
                stock_status, is_featured, primary_photo, piece_id
            ))
            conn.commit()

            log_activity(
                "Updated Piece", "Pieces",
                entity_type="Product", entity_id=piece_id,
                details=f"Modified jewellery specifications for '{name}'",
                old_val=f"₹{piece['price']:,.2f}", new_val=f"₹{price:,.2f}"
            )
            flash(f"Piece '{name}' updated successfully.", "success")
            return redirect(url_for('pieces_list'))

        cur.execute("SELECT * FROM categories ORDER BY name ASC;")
        categories = cur.fetchall()

        cur.execute("""
            SELECT * FROM activity_logs 
            WHERE entity_type = 'Product' AND entity_id = ?
            ORDER BY id DESC LIMIT 10;
        """, (piece_id,))
        history = cur.fetchall()

    return render_template(
        'piece_form.html',
        is_edit=True,
        piece=piece,
        categories=categories,
        history=history
    )

@app.route('/pieces/duplicate/<int:piece_id>')
@login_required
@role_required(['owner', 'manager'])
def piece_duplicate(piece_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = ?;", (piece_id,))
        p = cur.fetchone()
        if not p:
            flash("Piece not found to duplicate.", "danger")
            return redirect(url_for('pieces_list'))

        new_name = f"{p['name']} (Copy)"
        new_slug = f"{p['slug']}-copy-{datetime.now().strftime('%M%S')}"

        cur.execute("""
            INSERT INTO products (
                name, slug, category_id, metal_type, gold_purity, collection_name,
                description, huid_number, certificate_file, gold_weight_grams,
                stone_value, making_charge_type, making_charge_value, price,
                stock_qty, low_stock_threshold, stock_status, is_featured,
                primary_image, is_deleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            new_name, new_slug, p['category_id'], p['metal_type'], p['gold_purity'],
            p['collection_name'], p['description'], p['huid_number'], p['certificate_file'],
            p['gold_weight_grams'], p['stone_value'], p['making_charge_type'],
            p['making_charge_value'], p['price'], p['stock_qty'], p['low_stock_threshold'],
            p['stock_status'], p['is_featured'], p['primary_image']
        ))
        new_id = cur.lastrowid
        conn.commit()

    log_activity("Duplicated Piece", "Pieces", entity_type="Product", entity_id=new_id, details=f"Cloned piece #{piece_id} as '{new_name}'")
    flash(f"Duplicated '{p['name']}' as new piece #{new_id}.", "success")
    return redirect(url_for('piece_edit', piece_id=new_id))

@app.route('/pieces/hide/<int:piece_id>', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def piece_toggle_visibility(piece_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, is_featured FROM products WHERE id = ?;", (piece_id,))
        p = cur.fetchone()
        if p:
            new_val = 0 if p['is_featured'] else 1
            cur.execute("UPDATE products SET is_featured = ? WHERE id = ?;", (new_val, piece_id))
            conn.commit()
            log_activity("Toggled Visibility", "Pieces", entity_type="Product", entity_id=piece_id, details=f"Featured state changed to {new_val}")
            flash(f"Visibility toggled for '{p['name']}'.", "success")
    return redirect(url_for('pieces_list'))

@app.route('/pieces/delete/<int:piece_id>', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def piece_soft_delete(piece_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM products WHERE id = ?;", (piece_id,))
        p = cur.fetchone()
        if p:
            cur.execute("UPDATE products SET is_deleted = 1 WHERE id = ?;", (piece_id,))
            conn.commit()
            log_activity("Soft Deleted Piece", "Pieces", entity_type="Product", entity_id=piece_id, details=f"Archived '{p['name']}' from active view")
            flash(f"Piece '{p['name']}' moved to removed archive. You can restore it anytime.", "success")
    return redirect(url_for('pieces_list'))

@app.route('/pieces/restore/<int:piece_id>', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def piece_restore(piece_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM products WHERE id = ?;", (piece_id,))
        p = cur.fetchone()
        if p:
            cur.execute("UPDATE products SET is_deleted = 0 WHERE id = ?;", (piece_id,))
            conn.commit()
            log_activity("Restored Piece", "Pieces", entity_type="Product", entity_id=piece_id, details=f"Restored '{p['name']}' back to active catalogue")
            flash(f"Piece '{p['name']}' restored to active catalogue.", "success")
    return redirect(url_for('pieces_list', archived=1))

# -------------------------------------------------------------
# Module 3: Stock Management
# -------------------------------------------------------------
@app.route('/stock')
@login_required
def stock_list():
    low_only = request.args.get('low_only') == '1'
    status_filter = request.args.get('status')

    with get_db() as conn:
        cur = conn.cursor()

        # Stats
        cur.execute("SELECT count(*) FROM products WHERE is_deleted = 0;")
        total_items = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM products WHERE is_deleted = 0 AND stock_qty <= low_stock_threshold;")
        low_stock_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM products WHERE is_deleted = 0 AND stock_status = 'Sold';")
        sold_count = cur.fetchone()[0]

        query = "SELECT * FROM products WHERE is_deleted = 0"
        params = []
        if low_only:
            query += " AND stock_qty <= low_stock_threshold"
        if status_filter:
            query += " AND stock_status = ?"
            params.append(status_filter)

        query += " ORDER BY stock_qty ASC, id DESC;"
        cur.execute(query, params)
        pieces = cur.fetchall()

        # Recent adjustments
        cur.execute("""
            SELECT sa.*, p.name as product_name
            FROM stock_adjustments sa
            JOIN products p ON sa.product_id = p.id
            ORDER BY sa.id DESC LIMIT 15;
        """)
        recent_adjustments = cur.fetchall()

    return render_template(
        'stock_list.html',
        pieces=pieces,
        total_items=total_items,
        low_stock_count=low_stock_count,
        sold_count=sold_count,
        low_only=low_only,
        status_filter=status_filter,
        recent_adjustments=recent_adjustments
    )

@app.route('/stock/adjust', methods=['POST'])
@login_required
def stock_adjust():
    product_id = request.form.get('product_id')
    new_qty = int(request.form.get('new_qty') or 0)
    reason = request.form.get('reason', '').strip()
    status_update = request.form.get('stock_status')

    if not reason:
        flash("Stock adjustment requires a clear reason for audit integrity.", "danger")
        return redirect(url_for('stock_list'))

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, stock_qty, stock_status FROM products WHERE id = ?;", (product_id,))
        prod = cur.fetchone()
        if not prod:
            flash("Piece not found.", "danger")
            return redirect(url_for('stock_list'))

        old_qty = prod['stock_qty']
        change_qty = new_qty - old_qty
        target_status = status_update or ('Sold' if new_qty == 0 else ('Available' if new_qty > 0 else prod['stock_status']))

        cur.execute("""
            UPDATE products 
            SET stock_qty = ?, stock_status = ? 
            WHERE id = ?;
        """, (new_qty, target_status, product_id))

        cur.execute("""
            INSERT INTO stock_adjustments (product_id, change_qty, new_qty, reason, staff_id, staff_name)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (product_id, change_qty, new_qty, reason, session.get('staff_id'), session.get('staff_name', 'Staff')))

        conn.commit()

    log_activity(
        "Adjusted Stock", "Stock",
        entity_type="Product", entity_id=product_id,
        details=f"Stock for '{prod['name']}' changed ({old_qty} -> {new_qty}). Reason: {reason}",
        old_val=old_qty, new_val=new_qty
    )
    flash(f"Stock for '{prod['name']}' updated to {new_qty} units ({target_status}).", "success")
    return redirect(url_for('stock_list'))

# -------------------------------------------------------------
# Module 4: Gold Rate and Prices
# -------------------------------------------------------------
@app.route('/gold-rate')
@app.route('/gold-rates')
@login_required
def gold_rates():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM gold_rates ORDER BY id DESC LIMIT 1;")
        current_rate = cur.fetchone()

        cur.execute("SELECT * FROM gold_rates ORDER BY id DESC LIMIT 20;")
        rate_history = cur.fetchall()

        cur.execute("SELECT count(*) FROM products WHERE is_deleted = 0;")
        linked_count = cur.fetchone()[0]

    return render_template(
        'gold_rates.html',
        current_rate=current_rate,
        rate_history=rate_history,
        linked_count=linked_count
    )

@app.route('/gold-rates/update', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def gold_rates_update():
    rate_24k = float(request.form.get('rate_24k') or 7850.0)
    rate_22k = float(request.form.get('rate_22k') or 7200.0)
    rate_18k = float(request.form.get('rate_18k') or 5890.0)
    rate_silver = float(request.form.get('rate_silver') or 92.0)
    notes = request.form.get('notes', 'Bench update')

    today_str = datetime.now().strftime('%Y-%m-%d')
    updater = session.get('staff_name', 'Owner')

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO gold_rates (rate_24k, rate_22k, rate_18k, rate_silver, effective_date, updated_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (rate_24k, rate_22k, rate_18k, rate_silver, today_str, updater, notes))
        conn.commit()

    log_activity(
        "Updated Gold Bullion Rates", "Gold Rates",
        details=f"22K: ₹{rate_22k}/g, 24K: ₹{rate_24k}/g, 18K: ₹{rate_18k}/g, Silver: ₹{rate_silver}/g",
        new_val=f"22K: ₹{rate_22k}"
    )
    flash(f"Today's official benchmark rates recorded: 22K at ₹{rate_22k:,.2f}/g.", "success")
    return redirect(url_for('gold_rates'))

@app.route('/gold-rate/update-quick', methods=['POST'])
@app.route('/gold-rates/update-inline', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def gold_rates_update_inline():
    rate_22k = float(request.form.get('rate_22k') or 7200.0)
    # Estimate 24K as 22k / 0.916
    rate_24k = round(rate_22k / 0.916, 1)
    rate_18k = round(rate_24k * 0.75, 1)
    today_str = datetime.now().strftime('%Y-%m-%d')
    updater = session.get('staff_name', 'Owner')

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO gold_rates (rate_24k, rate_22k, rate_18k, rate_silver, effective_date, updated_by, notes)
            VALUES (?, ?, ?, 92.0, ?, ?, 'In-place quick dashboard update');
        """, (rate_24k, rate_22k, rate_18k, today_str, updater))
        conn.commit()

    log_activity("Updated Gold Rate from Dashboard", "Gold Rates", new_val=f"22K: ₹{rate_22k}")
    flash(f"Today's 22K gold benchmark set to ₹{rate_22k:,.2f}/g.", "success")
    return redirect(url_for('today'))

@app.route('/gold-rates/apply-all', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def gold_rates_apply_all():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT rate_22k, rate_18k, rate_24k FROM gold_rates ORDER BY id DESC LIMIT 1;")
        rates = cur.fetchone()
        if not rates:
            flash("No gold rate configured to apply.", "danger")
            return redirect(url_for('gold_rates'))

        cur.execute("SELECT * FROM products WHERE is_deleted = 0;")
        prods = cur.fetchall()

        updated_count = 0
        for p in prods:
            weight = p['gold_weight_grams'] or 14.5
            metal = p['metal_type'] or 'yellow_gold'
            if 'rose' in metal:
                rate = rates['rate_18k']
            elif 'platinum' in metal:
                rate = rates['rate_24k'] * 0.95
            else:
                rate = rates['rate_22k']

            metal_cost = weight * rate
            stone = p['stone_value'] or 0.0
            mc_val = p['making_charge_value'] or 12.0
            mc_type = p['making_charge_type'] or 'percent'

            if mc_type == 'percent':
                making_charge = metal_cost * (mc_val / 100.0)
            else:
                making_charge = mc_val

            subtotal = metal_cost + making_charge + stone
            new_price = round(subtotal * 1.03) # 3% GST

            cur.execute("UPDATE products SET price = ? WHERE id = ?;", (new_price, p['id']))
            updated_count += 1

        conn.commit()

    log_activity(
        "Mass Applied Gold Rate to Store", "Gold Rates",
        details=f"Recalculated prices for {updated_count} pieces using 22K rate ₹{rates['rate_22k']:,.2f}/g"
    )
    flash(f"Applied live benchmark to all {updated_count} store pieces successfully.", "success")
    return redirect(url_for('gold_rates'))

# -------------------------------------------------------------
# Module 5: Orders & Invoices
# -------------------------------------------------------------
@app.route('/orders')
@login_required
def orders_list():
    status_filter = request.args.get('status')
    
    with get_db() as conn:
        cur = conn.cursor()
        
        # Status counts
        cur.execute("SELECT status, count(*) FROM orders GROUP BY status;")
        counts_dict = dict(cur.fetchall())
        
        query = "SELECT * FROM orders"
        params = []
        if status_filter:
            query += " WHERE status = ?"
            params.append(status_filter)
        query += " ORDER BY id DESC;"

        cur.execute(query, params)
        orders = cur.fetchall()

    return render_template(
        'orders_list.html',
        orders=orders,
        selected_status=status_filter,
        status_counts=counts_dict
    )

@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE id = ?;", (order_id,))
        order = cur.fetchone()
        if not order:
            flash("Order not found.", "danger")
            return redirect(url_for('orders_list'))

        cur.execute("""
            SELECT oi.*, oi.price as price_at_purchase, p.name as product_name, p.primary_image, p.gold_weight_grams, p.metal_type, p.huid_number
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?;
        """, (order_id,))
        items = cur.fetchall()

    return render_template('order_detail.html', order=order, items=items)

@app.route('/orders/<int:order_id>/update-status', methods=['POST'])
@login_required
def order_update_status(order_id):
    new_status = request.form.get('status')
    bench_notes = request.form.get('bench_notes')

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT status FROM orders WHERE id = ?;", (order_id,))
        ord_row = cur.fetchone()
        if ord_row:
            old_status = ord_row['status']
            cur.execute("""
                UPDATE orders SET status = ?, bench_notes = COALESCE(?, bench_notes)
                WHERE id = ?;
            """, (new_status, bench_notes, order_id))
            conn.commit()

            log_activity(
                "Updated Order Status", "Orders",
                entity_type="Order", entity_id=order_id,
                details=f"Order #{order_id} moved to '{new_status}'",
                old_val=old_status, new_val=new_status
            )
            flash(f"Order #{order_id} status updated to {new_status.title()}.", "success")

    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/orders/<int:order_id>/update-shipping', methods=['POST'])
@login_required
def order_update_shipping(order_id):
    courier_name = request.form.get('courier_name')
    tracking_number = request.form.get('tracking_number')
    insured_value = float(request.form.get('insured_value') or 0.0)
    dispatch_date = request.form.get('dispatch_date')
    delivery_status = request.form.get('delivery_status')

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE orders SET
                courier_name = ?, tracking_number = ?, insured_value = ?,
                dispatch_date = ?, delivery_status = ?
            WHERE id = ?;
        """, (courier_name, tracking_number, insured_value, dispatch_date, delivery_status, order_id))
        conn.commit()

    log_activity(
        "Updated Armored Dispatch", "Delivery",
        entity_type="Order", entity_id=order_id,
        details=f"Assigned {courier_name} (Docket: {tracking_number}) for Order #{order_id}"
    )
    flash(f"Shipment details updated for Order #{order_id}.", "success")
    return redirect(url_for('order_detail', order_id=order_id))

@app.route('/orders/<int:order_id>/invoice')
@login_required
def order_invoice(order_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE id = ?;", (order_id,))
        order = cur.fetchone()
        if not order:
            abort(404)

        cur.execute("""
            SELECT oi.*, oi.price as price_at_purchase, p.name as product_name, p.gold_weight_grams, p.metal_type, p.huid_number
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?;
        """, (order_id,))
        items = cur.fetchall()

        cur.execute("SELECT setting_key, setting_value FROM store_settings;")
        settings = dict(cur.fetchall())

    return render_template('order_invoice.html', order=order, items=items, settings=settings)

# -------------------------------------------------------------
# Module 6: Delivery & Shipments
# -------------------------------------------------------------
@app.route('/delivery')
@login_required
def delivery_list():
    status_filter = request.args.get('status')

    with get_db() as conn:
        cur = conn.cursor()

        cur.execute("SELECT count(*) FROM orders WHERE delivery_status = 'Processing';")
        awaiting_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM orders WHERE delivery_status IN ('Dispatched', 'In Transit');")
        in_transit_count = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM orders WHERE delivery_status = 'Delivered';")
        delivered_count = cur.fetchone()[0]

        query = "SELECT * FROM orders WHERE 1=1"
        params = []
        if status_filter:
            query += " AND delivery_status = ?"
            params.append(status_filter)
        query += " ORDER BY id DESC;"

        cur.execute(query, params)
        shipments = cur.fetchall()

    return render_template(
        'delivery_list.html',
        shipments=shipments,
        selected_status=status_filter,
        awaiting_count=awaiting_count,
        in_transit_count=in_transit_count,
        delivered_count=delivered_count
    )

# -------------------------------------------------------------
# Module 7: Appointments & Custom Requests
# -------------------------------------------------------------
@app.route('/appointments-custom')
@login_required
def appointments_custom():
    tab = request.args.get('tab', 'requests')

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM custom_requests ORDER BY id DESC;")
        custom_requests = cur.fetchall()

        cur.execute("SELECT * FROM appointments ORDER BY preferred_date DESC, id DESC;")
        appointments = cur.fetchall()

    return render_template(
        'appointments_custom.html',
        active_tab=tab,
        custom_requests=custom_requests,
        appointments=appointments
    )

@app.route('/appointments-custom/new-request', methods=['POST'])
@login_required
def appointments_custom_new_request():
    client_name = request.form.get('client_name')
    client_phone = request.form.get('client_phone')
    client_email = request.form.get('client_email')
    piece_type = request.form.get('piece_type')
    description = request.form.get('description')
    target_date = request.form.get('target_date')
    quoted_price = float(request.form.get('quoted_price') or 0.0)
    advance_paid = float(request.form.get('advance_paid') or 0.0)
    balance_due = quoted_price - advance_paid

    photo_path = None
    if 'reference_photo' in request.files:
        file = request.files['reference_photo']
        if file and file.filename:
            fname = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, fname))
            photo_path = f'/static/products/{fname}'

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO custom_requests (
                client_name, client_phone, client_email, piece_type, reference_photo,
                description, quoted_price, advance_paid, balance_due, status, target_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'quoted' if ? > 0 else 'new', ?)
        """, (
            client_name, client_phone, client_email, piece_type, photo_path,
            description, quoted_price, advance_paid, balance_due, quoted_price, target_date
        ))
        conn.commit()

    log_activity(
        "Recorded Bespoke Request", "Appointments and Custom",
        details=f"Client '{client_name}' requested '{piece_type}' (Quote: ₹{quoted_price:,.2f})"
    )
    flash(f"Bespoke request for {client_name} registered.", "success")
    return redirect(url_for('appointments_custom', tab='requests'))

@app.route('/appointments-custom/update-request', methods=['POST'])
@login_required
def appointments_custom_update_request():
    req_id = request.form.get('request_id')
    status = request.form.get('status')
    quoted_price = float(request.form.get('quoted_price') or 0.0)
    advance_paid = float(request.form.get('advance_paid') or 0.0)
    karigar_notes = request.form.get('karigar_notes')
    balance_due = quoted_price - advance_paid

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE custom_requests SET
                status = ?, quoted_price = ?, advance_paid = ?, balance_due = ?, karigar_notes = ?
            WHERE id = ?;
        """, (status, quoted_price, advance_paid, balance_due, karigar_notes, req_id))
        conn.commit()

    log_activity("Updated Bespoke Commission", "Appointments and Custom", entity_type="CustomRequest", entity_id=req_id, details=f"Status: {status}, Advance: ₹{advance_paid}")
    flash("Bespoke commission updated.", "success")
    return redirect(url_for('appointments_custom', tab='requests'))

# -------------------------------------------------------------
# Module 8: Website Photos and Text
# -------------------------------------------------------------
@app.route('/website-content')
@login_required
def website_content():
    with get_db() as conn:
        cur = conn.cursor()
        
        cur.execute("SELECT setting_key, setting_value FROM store_settings;")
        settings = dict(cur.fetchall())

        cur.execute("SELECT * FROM customer_stories ORDER BY sort_order ASC, id ASC;")
        stories = cur.fetchall()

        cur.execute("SELECT * FROM faq_items ORDER BY sort_order ASC, id ASC;")
        faqs = cur.fetchall()

        cur.execute("SELECT * FROM website_content_history ORDER BY id DESC LIMIT 10;")
        history = cur.fetchall()

    return render_template(
        'website_content.html',
        settings=settings,
        stories=stories,
        faqs=faqs,
        history=history
    )

@app.route('/website-content/announcement', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def website_announcement():
    text = request.form.get('announcement_bar_text', '').strip()
    link = request.form.get('announcement_bar_link', '').strip()

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO store_settings (setting_key, setting_value) VALUES ('announcement_bar_text', ?);", (text,))
        cur.execute("INSERT OR REPLACE INTO store_settings (setting_key, setting_value) VALUES ('announcement_bar_link', ?);", (link,))
        
        # Save history snapshot
        cur.execute("""
            INSERT INTO website_content_history (section_key, content_json, version_number, created_by)
            VALUES ('announcement_bar', ?, (SELECT count(*) + 1 FROM website_content_history WHERE section_key = 'announcement_bar'), ?)
        """, (json.dumps({'text': text, 'link': link}), session.get('staff_name', 'Admin')))
        conn.commit()

    log_activity("Updated Announcement Bar", "Website Content", details=f"New text: {text}")
    flash("Homepage announcement bar updated.", "success")
    return redirect(url_for('website_content'))

@app.route('/website-content/stories/add', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def website_story_add():
    occasion = request.form.get('occasion')
    quote = request.form.get('quote')
    client_name = request.form.get('client_name')
    city = request.form.get('city')
    piece_name = request.form.get('piece_name')
    year = int(request.form.get('year') or 2025)

    photo_path = '/static/lifestyle/lifestyle-product-1.webp'
    if 'story_photo' in request.files:
        file = request.files['story_photo']
        if file and file.filename:
            fname = secure_filename(file.filename)
            file.save(os.path.join(LIFESTYLE_FOLDER, fname))
            photo_path = f'/static/lifestyle/{fname}'

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO customer_stories (occasion, quote, client_name, city, piece_name, year, photo_path, is_approved, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, (SELECT count(*) + 1 FROM customer_stories));
        """, (occasion, quote, client_name, city, piece_name, year, photo_path))
        conn.commit()

    log_activity("Added Family Album Story", "Website Content", details=f"Added occasion '{occasion}' for {client_name}")
    flash(f"Family story '{occasion}' published to store.", "success")
    return redirect(url_for('website_content'))

@app.route('/website-content/stories/toggle/<int:story_id>', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def website_story_toggle(story_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT occasion, is_approved FROM customer_stories WHERE id = ?;", (story_id,))
        s = cur.fetchone()
        if s:
            new_val = 0 if s['is_approved'] else 1
            cur.execute("UPDATE customer_stories SET is_approved = ? WHERE id = ?;", (new_val, story_id))
            conn.commit()
            flash("Story visibility updated.", "success")
    return redirect(url_for('website_content'))

@app.route('/website-content/stories/delete/<int:story_id>', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def website_story_delete(story_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM customer_stories WHERE id = ?;", (story_id,))
        conn.commit()
        flash("Story removed from store.", "success")
    return redirect(url_for('website_content'))

@app.route('/website-content/faq/add', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def website_faq_add():
    question = request.form.get('question')
    answer = request.form.get('answer')
    sort_order = int(request.form.get('sort_order') or 10)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO faq_items (question, answer, is_active, sort_order)
            VALUES (?, ?, 1, ?);
        """, (question, answer, sort_order))
        conn.commit()

    log_activity("Added FAQ Item", "Website Content", details=f"Added question: '{question}'")
    flash("Bench answer added to FAQ.", "success")
    return redirect(url_for('website_content'))

@app.route('/website-content/faq/edit', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def website_faq_edit():
    faq_id = request.form.get('faq_id')
    question = request.form.get('question')
    answer = request.form.get('answer')
    sort_order = int(request.form.get('sort_order') or 1)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE faq_items SET question = ?, answer = ?, sort_order = ?
            WHERE id = ?;
        """, (question, answer, sort_order, faq_id))
        conn.commit()

    log_activity("Edited FAQ Item", "Website Content", entity_type="FAQ", entity_id=faq_id, details=f"Edited question: '{question}'")
    flash("FAQ item updated.", "success")
    return redirect(url_for('website_content'))

@app.route('/website-content/revert/<int:history_id>', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def website_content_revert(history_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM website_content_history WHERE id = ?;", (history_id,))
        h = cur.fetchone()
        if h:
            data = json.loads(h['content_json'])
            if h['section_key'] == 'announcement_bar':
                cur.execute("INSERT OR REPLACE INTO store_settings (setting_key, setting_value) VALUES ('announcement_bar_text', ?);", (data.get('text'),))
                cur.execute("INSERT OR REPLACE INTO store_settings (setting_key, setting_value) VALUES ('announcement_bar_link', ?);", (data.get('link'),))
                conn.commit()
                flash(f"Reverted announcement bar to version v{h['version_number']}.", "success")
    return redirect(url_for('website_content'))

# -------------------------------------------------------------
# Module 9: Customers
# -------------------------------------------------------------
@app.route('/customers')
@login_required
def customers_list():
    vip_only = request.args.get('vip') == '1'

    with get_db() as conn:
        cur = conn.cursor()
        query = """
            SELECT cp.*, 
                   COUNT(o.id) as order_count, 
                   COALESCE(SUM(o.total_amount), 0) as total_spent
            FROM customer_profiles cp
            LEFT JOIN orders o ON lower(o.customer_phone) = lower(cp.phone)
        """
        params = []
        if vip_only:
            query += " WHERE cp.is_vip = 1"
        query += " GROUP BY cp.id ORDER BY cp.id DESC;"

        cur.execute(query, params)
        customers = cur.fetchall()

    return render_template('customers_list.html', customers=customers)

@app.route('/customers/new', methods=['POST'])
@login_required
def customers_new():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    city = request.form.get('city')
    family_occasions = request.form.get('family_occasions')
    notes = request.form.get('notes')
    is_vip = int(request.form.get('is_vip') or 0)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO customer_profiles (name, phone, email, city, family_occasions, notes, is_vip)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (name, phone, email, city, family_occasions, notes, is_vip))
        conn.commit()

    log_activity("Created Patron Profile", "Customers", details=f"Added profile for '{name}' ({phone})")
    flash(f"Patron profile '{name}' saved.", "success")
    return redirect(url_for('customers_list'))

@app.route('/customers/edit', methods=['POST'])
@login_required
def customers_edit():
    cust_id = request.form.get('customer_id')
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    city = request.form.get('city')
    family_occasions = request.form.get('family_occasions')
    notes = request.form.get('notes')
    is_vip = int(request.form.get('is_vip') or 0)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE customer_profiles SET
                name = ?, phone = ?, email = ?, city = ?,
                family_occasions = ?, notes = ?, is_vip = ?
            WHERE id = ?;
        """, (name, phone, email, city, family_occasions, notes, is_vip, cust_id))
        conn.commit()

    log_activity("Updated Patron Profile", "Customers", entity_type="Customer", entity_id=cust_id, details=f"Updated profile for '{name}'")
    flash(f"Profile '{name}' updated.", "success")
    return redirect(url_for('customers_list'))

# -------------------------------------------------------------
# Module 10: Reports & Analytics
# -------------------------------------------------------------
@app.route('/reports')
@login_required
def reports():
    with get_db() as conn:
        cur = conn.cursor()

        # Total revenue
        cur.execute("SELECT COALESCE(SUM(total_amount), 0), count(*) FROM orders WHERE status NOT IN ('cancelled', 'returned');")
        rev_row = cur.fetchone()
        total_revenue = rev_row[0]
        total_orders = rev_row[1]

        # Inventory gold valuation
        cur.execute("SELECT COALESCE(SUM(gold_weight_grams * stock_qty), 0), count(*) FROM products WHERE is_deleted = 0;")
        inv_row = cur.fetchone()
        total_gold_weight = inv_row[0]
        active_pieces_count = inv_row[1]

        cur.execute("SELECT rate_22k FROM gold_rates ORDER BY id DESC LIMIT 1;")
        r_row = cur.fetchone()
        r22 = r_row['rate_22k'] if r_row else 7200.0
        total_inventory_value = total_gold_weight * r22

        # GST calculation: Total GST = Revenue - (Revenue / 1.03)
        taxable_value = total_revenue / 1.03
        total_gst = total_revenue - taxable_value

        # Sales by Category
        cur.execute("""
            SELECT c.name as category_name, COUNT(oi.id) as units_sold, COALESCE(SUM(oi.price * oi.quantity), 0) as total_amount
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status NOT IN ('cancelled', 'returned')
            GROUP BY c.id
            ORDER BY total_amount DESC;
        """)
        category_sales = cur.fetchall()

        # Best sellers
        cur.execute("""
            SELECT p.name as product_name, SUM(oi.quantity) as total_qty, SUM(oi.price * oi.quantity) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status NOT IN ('cancelled', 'returned')
            GROUP BY p.id
            ORDER BY total_qty DESC, total_revenue DESC LIMIT 5;
        """)
        best_sellers = cur.fetchall()

        # Monthly breakdown
        cur.execute("""
            SELECT strftime('%Y-%m', created_at) as month_label,
                   COUNT(id) as order_count,
                   SUM(total_amount) as gross_total
            FROM orders
            WHERE status NOT IN ('cancelled', 'returned')
            GROUP BY month_label
            ORDER BY month_label DESC;
        """)
        m_rows = cur.fetchall()
        monthly_sales = []
        for mr in m_rows:
            gross = mr['gross_total'] or 0
            taxable = gross / 1.03
            gst_tot = gross - taxable
            monthly_sales.append({
                'month_label': mr['month_label'] or 'Recent',
                'order_count': mr['order_count'],
                'gross_total': gross,
                'taxable_value': taxable,
                'cgst': gst_tot / 2.0,
                'sgst': gst_tot / 2.0
            })

    return render_template(
        'reports.html',
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_gold_weight=total_gold_weight,
        active_pieces_count=active_pieces_count,
        total_inventory_value=total_inventory_value,
        total_gst=total_gst,
        category_sales=category_sales,
        best_sellers=best_sellers,
        monthly_sales=monthly_sales
    )

@app.route('/reports/export-csv')
@login_required
def reports_export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Order ID', 'Date', 'Customer Name', 'Phone', 'Items Count', 'Gross Amount (INR)', 'Taxable Value', 'GST (3%)', 'Status', 'Courier'])

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders ORDER BY id DESC;")
        orders = cur.fetchall()
        for o in orders:
            gross = o['total_amount'] or 0
            taxable = round(gross / 1.03, 2)
            gst = round(gross - taxable, 2)
            writer.writerow([o['id'], o['created_at'][:10], o['customer_name'], o['customer_phone'], 1, gross, taxable, gst, o['status'], o['courier_name']])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=atelier_nilaya_sales_report.csv"}
    )

# -------------------------------------------------------------
# Module 11: Settings & Staff Management
# -------------------------------------------------------------
@app.route('/settings')
@login_required
def settings_page():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT setting_key, setting_value FROM store_settings;")
        settings = dict(cur.fetchall())

        cur.execute("SELECT * FROM staff_users ORDER BY id ASC;")
        staff_list = cur.fetchall()

    return render_template('settings.html', settings=settings, staff_list=staff_list)

@app.route('/settings/update-business', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def settings_update_business():
    fields = [
        'business_name', 'founded_year', 'showroom_address', 'contact_phone',
        'contact_email', 'gst_number', 'whatsapp_number', 'courier_partners',
        'payment_gateway', 'brand_serif_font'
    ]
    with get_db() as conn:
        cur = conn.cursor()
        for field in fields:
            val = request.form.get(field, '').strip()
            cur.execute("INSERT OR REPLACE INTO store_settings (setting_key, setting_value) VALUES (?, ?);", (field, val))
        conn.commit()

    log_activity("Updated Business Settings", "Settings", details="Updated business legal profile and integration placeholders")
    flash("Business details and integrations saved successfully.", "success")
    return redirect(url_for('settings_page'))

@app.route('/settings/new-staff', methods=['POST'])
@login_required
@role_required(['owner', 'manager'])
def settings_new_staff():
    name = request.form.get('name')
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password')
    role = request.form.get('role', 'manager')
    phone = request.form.get('phone')

    # Security check: only Owner can create other Owners
    if role == 'owner' and session.get('staff_role') != 'owner':
        flash("Only the Owner can grant Owner privileges.", "danger")
        return redirect(url_for('settings_page'))

    with get_db() as conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO staff_users (email, name, password_hash, role, phone, two_factor_enabled, two_factor_secret)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (email, name, hash_pwd(password), role, phone, 1 if role == 'owner' else 0, '729401' if role == 'owner' else None))
            conn.commit()
            log_activity("Created Staff Account", "Settings", details=f"Added staff member '{name}' with role '{role}'")
            flash(f"Staff account for {name} ({role}) created.", "success")
        except sqlite3.IntegrityError:
            flash(f"Staff email '{email}' already registered.", "danger")

    return redirect(url_for('settings_page'))

@app.route('/settings/backup-db')
@login_required
@role_required(['owner'])
def settings_backup_db():
    log_activity("Downloaded Database Backup", "Settings", details="Owner exported nilaya.db snapshot")
    return send_file(DB_PATH, as_attachment=True, download_name=f"nilaya_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")

# -------------------------------------------------------------
# Module 12: Activity Logs
# -------------------------------------------------------------
@app.route('/activity-logs')
@login_required
def activity_logs_view():
    module_filter = request.args.get('module')

    with get_db() as conn:
        cur = conn.cursor()
        query = "SELECT * FROM activity_logs WHERE 1=1"
        params = []
        if module_filter:
            query += " AND module = ?"
            params.append(module_filter)
        query += " ORDER BY id DESC LIMIT 100;"

        cur.execute(query, params)
        logs = cur.fetchall()

    return render_template('activity_logs.html', logs=logs, selected_module=module_filter)

@app.errorhandler(500)
def internal_error(error):
    import traceback
    err_trace = traceback.format_exc()
    print("500 INTERNAL SERVER ERROR:\n", err_trace)
    return f"""<!DOCTYPE html>
<html>
<head><title>Admin Notice &bull; Atelier Nilaya</title>
<style>body{{font-family:sans-serif;padding:32px;background:#f6f1e7;color:#2b1a1f;}}pre{{background:#fff;padding:16px;border:1px solid #e0d8ce;border-radius:6px;overflow:auto;}}</style>
</head>
<body>
<h2>Atelier Nilaya Admin &bull; Application Notice</h2>
<p>The application encountered an unexpected condition. Diagnostic details:</p>
<pre>{err_trace if err_trace.strip() != 'NoneType: None' else str(error)}</pre>
<p><a href="/today">Return to Today Dashboard</a> &bull; <a href="/login">Re-login</a></p>
</body>
</html>""", 500

# -------------------------------------------------------------
# Main Application Runner
# -------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("ATELIER NILAYA (SURAT, EST. 1954) — ADMIN APP")
    print("Running secure admin portal on port 8080...")
    print("URL: http://127.0.0.1:8080/")
    print("Owner Account: owner@ateliernilaya.com | OTP: 729401")
    print("=" * 60)
    app.run(host='127.0.0.1', port=8080, debug=False)
