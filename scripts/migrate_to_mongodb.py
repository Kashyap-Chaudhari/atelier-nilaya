#!/usr/bin/env python3
"""
Production-grade Relational to MongoDB Migration Script for Atelier Nilaya.
Streams batches, embeds denormalized child entities (profiles, addresses, order items, payments, shipment),
preserves Decimal128 precision, sets indexes, and provides idempotent upsert with resumability.
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from bson.decimal128 import Decimal128
from pymongo import MongoClient, UpdateOne, ASCENDING, DESCENDING, TEXT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scripts/migration.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Migrator")

SOURCE_DB_PATH = "db.sqlite3"
MONGO_URI = "mongodb://127.0.0.1:27017"
MONGO_DB_NAME = "nilaya_atelier"
BATCH_SIZE = 1000
PROGRESS_FILE = "scripts/migration_checkpoint.json"

def get_mongo_client():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[MONGO_DB_NAME]

def get_source_connection():
    conn = sqlite3.connect(SOURCE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def to_decimal(val):
    if val is None or val == "":
        return Decimal128("0.00")
    try:
        return Decimal128(Decimal(str(val)))
    except Exception:
        return Decimal128("0.00")

def to_datetime(val):
    if not val:
        return None
    if isinstance(val, str):
        val = val.replace(" ", "T")
        if not val.endswith("Z") and "+" not in val:
            val += "Z"
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        except ValueError:
            return None
    return val

def load_checkpoint():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_user_id": 0, "last_product_id": 0, "last_order_id": 0, "last_campaign_id": 0}

def save_checkpoint(stage, last_id):
    state = load_checkpoint()
    state[stage] = last_id
    with open(PROGRESS_FILE, "w") as f:
        json.dump(state, f, indent=2)

def create_indexes(db):
    logger.info("Ensuring MongoDB collection indexes...")
    # Users
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.users.create_index([("profile.mobile_number", ASCENDING)], sparse=True)
    
    # Products
    db.products.create_index([("slug", ASCENDING)], unique=True)
    db.products.create_index([("sku", ASCENDING)], unique=True)
    db.products.create_index([("category.slug", ASCENDING), ("flags.is_active", ASCENDING), ("created_at", DESCENDING)])
    db.products.create_index([("flags.is_active", ASCENDING), ("pricing.base_metal", ASCENDING)])
    db.products.create_index([("name", TEXT), ("specifications.gemstone_details", TEXT)])
    
    # Orders
    db.orders.create_index([("order_number", ASCENDING)], unique=True)
    db.orders.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    db.orders.create_index([("customer.email", ASCENDING), ("created_at", DESCENDING)])
    db.orders.create_index([("status", ASCENDING), ("created_at", DESCENDING)])
    db.orders.create_index([("payments.razorpay_order_id", ASCENDING)])
    
    # TTL Indexes
    db.stock_reservations.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    db.customer_phone_otps.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    logger.info("Indexes successfully configured.")

def migrate_users(source_conn, mongo_db):
    logger.info("=== Migrating Users (auth_user + profile + addresses) ===")
    checkpoint = load_checkpoint()
    last_id = checkpoint.get("last_user_id", 0)

    cur = source_conn.cursor()
    total_migrated = 0
    while True:
        cur.execute("""
            SELECT u.id, u.username, u.email, u.password, u.first_name, u.last_name,
                   u.is_staff, u.is_active, u.date_joined, u.last_login,
                   p.mobile_number, p.is_email_verified, p.failed_login_attempts, p.locked_until
            FROM auth_user u
            LEFT JOIN campaigns_userprofile p ON u.id = p.user_id
            WHERE u.id > ?
            ORDER BY u.id ASC
            LIMIT ?
        """, (last_id, BATCH_SIZE))
        users = cur.fetchall()
        if not users:
            break

        user_ids = [u["id"] for u in users]
        
        # Prefetch addresses for this batch
        cur.execute(f"""
            SELECT id, user_id, full_name, phone, address_line1, address_line2,
                   city, state, pincode, is_default
            FROM orders_shippingaddress
            WHERE user_id IN ({','.join(['?']*len(user_ids))})
        """, user_ids)
        addresses_by_user = {}
        for addr in cur.fetchall():
            addresses_by_user.setdefault(addr["user_id"], []).append({
                "address_id": addr["id"],
                "full_name": addr["full_name"],
                "phone": addr["phone"],
                "address_line1": addr["address_line1"],
                "address_line2": addr["address_line2"] or "",
                "city": addr["city"],
                "state": addr["state"],
                "pincode": addr["pincode"],
                "is_default": bool(addr["is_default"])
            })

        operations = []
        for u in users:
            doc = {
                "_id": u["id"],
                "username": u["username"],
                "email": u["email"],
                "password_hash": u["password"],
                "first_name": u["first_name"] or "",
                "last_name": u["last_name"] or "",
                "is_staff": bool(u["is_staff"]),
                "is_active": bool(u["is_active"]),
                "date_joined": to_datetime(u["date_joined"]),
                "last_login": to_datetime(u["last_login"]),
                "profile": {
                    "mobile_number": u["mobile_number"] or "",
                    "is_email_verified": bool(u["is_email_verified"]) if u["is_email_verified"] is not None else False,
                    "failed_login_attempts": u["failed_login_attempts"] or 0,
                    "locked_until": to_datetime(u["locked_until"])
                },
                "addresses": addresses_by_user.get(u["id"], [])
            }
            operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))

        if operations:
            mongo_db.users.bulk_write(operations, ordered=False)
            total_migrated += len(operations)
            last_id = user_ids[-1]
            save_checkpoint("last_user_id", last_id)

    logger.info(f"Users migration complete. Total: {total_migrated}")

def migrate_categories_and_products(source_conn, mongo_db):
    logger.info("=== Migrating Products & Categories ===")
    checkpoint = load_checkpoint()
    last_id = checkpoint.get("last_product_id", 0)

    cur = source_conn.cursor()
    total_migrated = 0
    while True:
        cur.execute("""
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM campaigns_jewelleryproduct p
            LEFT JOIN campaigns_jewellerycategory c ON p.category_id = c.id
            WHERE p.id > ?
            ORDER BY p.id ASC
            LIMIT ?
        """, (last_id, BATCH_SIZE))
        products = cur.fetchall()
        if not products:
            break

        operations = []
        for p in products:
            avail_sizes = [s.strip() for s in p["available_sizes"].split(",")] if p["available_sizes"] else []
            doc = {
                "_id": p["id"],
                "name": p["name"],
                "slug": p["slug"],
                "sku": p["sku"],
                "eyebrow": p["eyebrow"] or "",
                "short_description": p["short_description"] or "",
                "description": p["description"] or "",
                "category": {
                    "id": p["category_id"],
                    "name": p["category_name"] or "Uncategorized",
                    "slug": p["category_slug"] or "uncategorized"
                },
                "pricing": {
                    "base_metal": p["base_metal"] or "yellow_gold",
                    "metal_purity": p["metal_purity"] or "18K",
                    "gold_weight_grams": to_decimal(p["gold_weight_grams"]),
                    "making_charge_type": p["making_charge_type"] or "fixed",
                    "making_charge_value": to_decimal(p["making_charge_value"]),
                    "stone_value": to_decimal(p["stone_value"]),
                    "advance_payment_percentage": to_decimal(p["advance_payment_percentage"])
                },
                "specifications": {
                    "gemstone_details": p["gemstone_details"] or "",
                    "huid_number": p["huid_number"] or "",
                    "available_sizes": avail_sizes
                },
                "inventory": {
                    "stock_quantity": p["stock_quantity"] or 0,
                    "is_in_stock": bool(p["is_in_stock"]),
                    "is_one_of_a_kind": bool(p["is_one_of_a_kind"]),
                    "is_made_to_order": bool(p["is_made_to_order"]),
                    "making_days": p["making_days"] or 0
                },
                "media": {
                    "primary_image": p["image_url_fallback"] or (f"/media/{p['image']}" if p["image"] else "")
                },
                "flags": {
                    "is_featured": bool(p["is_featured"]),
                    "is_bestseller": bool(p["is_bestseller"]),
                    "is_active": True
                },
                "created_at": to_datetime(p["created_at"])
            }
            operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))

        if operations:
            mongo_db.products.bulk_write(operations, ordered=False)
            total_migrated += len(operations)
            last_id = products[-1]["id"]
            save_checkpoint("last_product_id", last_id)

    logger.info(f"Products migration complete. Total: {total_migrated}")

def migrate_orders(source_conn, mongo_db):
    logger.info("=== Migrating Orders (Order + Items + Payments + History + Shipment) ===")
    checkpoint = load_checkpoint()
    last_id = checkpoint.get("last_order_id", 0)

    cur = source_conn.cursor()
    total_migrated = 0
    while True:
        cur.execute("""
            SELECT o.*,
                   s.courier_name, s.tracking_number, s.tracking_url,
                   s.status as shipment_status, s.requires_delivery_otp, s.dispatch_date
            FROM orders_order o
            LEFT JOIN shipping_shipment s ON o.id = s.order_id
            WHERE o.id > ?
            ORDER BY o.id ASC
            LIMIT ?
        """, (last_id, BATCH_SIZE))
        orders = cur.fetchall()
        if not orders:
            break

        order_ids = [o["id"] for o in orders]

        # Prefetch Items
        cur.execute(f"""
            SELECT * FROM orders_orderitem
            WHERE order_id IN ({','.join(['?']*len(order_ids))})
        """, order_ids)
        items_by_order = {}
        for it in cur.fetchall():
            items_by_order.setdefault(it["order_id"], []).append({
                "product_id": it["product_id"],
                "product_name": it["product_name"],
                "sku": it["sku"],
                "metal": it["metal"],
                "size": it["size"],
                "engraving_text": it["engraving_text"] or "",
                "gold_weight_grams": to_decimal(it["gold_weight_grams"]),
                "gold_value": to_decimal(it["gold_value"]),
                "making_charge": to_decimal(it["making_charge"]),
                "stone_value": to_decimal(it["stone_value"]),
                "gst_amount": to_decimal(it["gst_amount"]),
                "unit_price": to_decimal(it["unit_price"]),
                "quantity": it["quantity"],
                "total_price": to_decimal(it["total_price"])
            })

        # Prefetch Payments
        cur.execute(f"""
            SELECT * FROM payments_payment
            WHERE order_id IN ({','.join(['?']*len(order_ids))})
        """, order_ids)
        payments_by_order = {}
        for pay in cur.fetchall():
            payments_by_order.setdefault(pay["order_id"], []).append({
                "razorpay_order_id": pay["razorpay_order_id"],
                "razorpay_payment_id": pay["razorpay_payment_id"] or "",
                "amount": to_decimal(pay["amount"]),
                "currency": pay["currency"] or "INR",
                "status": pay["status"],
                "created_at": to_datetime(pay["created_at"])
            })

        # Prefetch Status History
        cur.execute(f"""
            SELECT * FROM orders_orderstatushistory
            WHERE order_id IN ({','.join(['?']*len(order_ids))})
            ORDER BY created_at ASC
        """, order_ids)
        history_by_order = {}
        for h in cur.fetchall():
            history_by_order.setdefault(h["order_id"], []).append({
                "status": h["status"],
                "comment": h["comment"] or "",
                "changed_by": h["changed_by"] or "system",
                "created_at": to_datetime(h["created_at"])
            })

        operations = []
        for o in orders:
            doc = {
                "_id": o["order_number"],
                "order_number": o["order_number"],
                "user_id": o["user_id"],
                "customer": {
                    "name": o["customer_name"],
                    "email": o["customer_email"],
                    "phone": o["customer_phone"]
                },
                "shipping_address_text": o["shipping_address_text"],
                "status": o["status"],
                "financials": {
                    "total_gold_value": to_decimal(o["total_gold_value"]),
                    "total_making_charge": to_decimal(o["total_making_charge"]),
                    "total_stone_value": to_decimal(o["total_stone_value"]),
                    "gst_amount": to_decimal(o["gst_amount"]),
                    "shipping_amount": to_decimal(o["shipping_amount"]),
                    "discount_amount": to_decimal(o["discount_amount"]),
                    "total_amount": to_decimal(o["total_amount"]),
                    "advance_amount_paid": to_decimal(o["advance_amount_paid"]),
                    "balance_amount_due": to_decimal(o["balance_amount_due"])
                },
                "is_made_to_order": bool(o["is_made_to_order"]),
                "is_gift": bool(o["is_gift"]),
                "gift_message": o["gift_message"] or "",
                "items": items_by_order.get(o["id"], []),
                "payments": payments_by_order.get(o["id"], []),
                "status_history": history_by_order.get(o["id"], []),
                "shipment": {
                    "courier_name": o["courier_name"] or "",
                    "tracking_number": o["tracking_number"] or "",
                    "tracking_url": o["tracking_url"] or "",
                    "status": o["shipment_status"] or "unfulfilled"
                } if o["courier_name"] else None,
                "created_at": to_datetime(o["created_at"]),
                "updated_at": to_datetime(o["updated_at"])
            }
            operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))

        if operations:
            mongo_db.orders.bulk_write(operations, ordered=False)
            total_migrated += len(operations)
            last_id = orders[-1]["id"]
            save_checkpoint("last_order_id", last_id)

    logger.info(f"Orders migration complete. Total: {total_migrated}")

def verify_migration(source_conn, mongo_db):
    logger.info("\n=== Post-Migration Verification Summary ===")
    cur = source_conn.cursor()
    
    # 1. Counts
    u_sql = cur.execute("SELECT COUNT(*) FROM auth_user").fetchone()[0]
    u_mg = mongo_db.users.count_documents({})
    p_sql = cur.execute("SELECT COUNT(*) FROM campaigns_jewelleryproduct").fetchone()[0]
    p_mg = mongo_db.products.count_documents({})
    o_sql = cur.execute("SELECT COUNT(*) FROM orders_order").fetchone()[0]
    o_mg = mongo_db.orders.count_documents({})
    
    print(f"Users Count:     SQL={u_sql} | Mongo={u_mg} -> {'MATCH' if u_sql == u_mg else 'MISMATCH'}")
    print(f"Products Count:  SQL={p_sql} | Mongo={p_mg} -> {'MATCH' if p_sql == p_mg else 'MISMATCH'}")
    print(f"Orders Count:    SQL={o_sql} | Mongo={o_mg} -> {'MATCH' if o_sql == o_mg else 'MISMATCH'}")
    
    # 2. Financial Revenue Checksum
    rev_sql = cur.execute("SELECT SUM(total_amount) FROM orders_order").fetchone()[0] or 0.0
    pipe = [{"$group": {"_id": None, "total": {"$sum": "$financials.total_amount"}}}]
    res = list(mongo_db.orders.aggregate(pipe))
    rev_mg = res[0]["total"].to_decimal() if res else Decimal("0.00")
    diff = abs(Decimal(str(rev_sql)) - rev_mg)
    print(f"Revenue Sum:     SQL=INR {rev_sql:.2f} | Mongo=INR {rev_mg} | Diff={diff} -> {'MATCH' if diff < Decimal('0.01') else 'FAIL'}")

def main():
    logger.info("Connecting to MongoDB and Source Database...")
    mongo_db = get_mongo_client()
    source_conn = get_source_connection()
    
    try:
        create_indexes(mongo_db)
        migrate_users(source_conn, mongo_db)
        migrate_categories_and_products(source_conn, mongo_db)
        migrate_orders(source_conn, mongo_db)
        verify_migration(source_conn, mongo_db)
        logger.info("ALL MIGRATIONS FINISHED SUCCESSFULLY.")
    except Exception as e:
        logger.error(f"Migration error: {e}", exc_info=True)
    finally:
        source_conn.close()

if __name__ == "__main__":
    main()
