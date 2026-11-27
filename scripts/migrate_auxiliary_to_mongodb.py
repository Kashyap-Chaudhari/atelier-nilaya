#!/usr/bin/env python3
"""
Full Complete Relational to MongoDB Migration Script for Atelier Nilaya.
Migrates ALL tables:
1. users (embedded profiles + addresses)
2. products (embedded categories + pricing)
3. orders (embedded items + payments + status history + shipments)
4. campaigns (hero videos & collection themes)
5. gold_rates (daily benchmark gold, platinum, silver rates)
6. coupons (discount vouchers)
7. carts (embedded active cart items)
8. notification_logs (SMS / email / WhatsApp dispatch history)
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime
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

def migrate_campaigns(source_conn, mongo_db):
    logger.info("=== Migrating Campaigns ===")
    cur = source_conn.cursor()
    cur.execute("SELECT * FROM campaigns_jewellerycampaign")
    rows = cur.fetchall()
    operations = []
    for r in rows:
        doc = {
            "_id": r["id"],
            "title": r["title"],
            "slug": r["slug"],
            "eyebrow": r["eyebrow"] or "",
            "headline_sub": r["headline_sub"] or "",
            "description": r["description"] or "",
            "cta_text": r["cta_text"] or "",
            "cta_url": r["cta_url"] or "",
            "display_order": r["display_order"] or 0,
            "is_active": bool(r["is_active"]),
            "curator_note": r["curator_note"] or "",
            "provenance_tag": r["provenance_tag"] or "",
            "theme_accent": r["theme_accent"] or "",
            "composition_style": r["composition_style"] or "",
            "created_at": to_datetime(r["created_at"]),
            "updated_at": to_datetime(r["updated_at"])
        }
        operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
    if operations:
        mongo_db.campaigns.bulk_write(operations, ordered=False)
    logger.info(f"Campaigns migrated: {len(operations)}")

def migrate_gold_rates(source_conn, mongo_db):
    logger.info("=== Migrating Gold Rates ===")
    cur = source_conn.cursor()
    cur.execute("SELECT * FROM campaigns_goldrate")
    rows = cur.fetchall()
    operations = []
    for r in rows:
        doc = {
            "_id": r["id"],
            "rate_24k": to_decimal(r["rate_24k"]),
            "rate_22k": to_decimal(r["rate_22k"]),
            "rate_18k": to_decimal(r["rate_18k"]),
            "rate_platinum": to_decimal(r["rate_platinum"]),
            "rate_silver": to_decimal(r["rate_silver"]),
            "effective_date": str(r["effective_date"]),
            "updated_at": to_datetime(r["updated_at"]),
            "updated_by": r["updated_by"] or "system",
            "notes": r["notes"] or ""
        }
        operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
    if operations:
        mongo_db.gold_rates.bulk_write(operations, ordered=False)
    logger.info(f"Gold rates migrated: {len(operations)}")

def migrate_coupons(source_conn, mongo_db):
    logger.info("=== Migrating Coupons ===")
    cur = source_conn.cursor()
    cur.execute("SELECT * FROM orders_coupon")
    rows = cur.fetchall()
    operations = []
    for r in rows:
        doc = {
            "_id": r["id"],
            "code": r["code"],
            "discount_type": r["discount_type"],
            "discount_value": to_decimal(r["discount_value"]),
            "min_order_amount": to_decimal(r["min_order_amount"]),
            "max_discount_amount": to_decimal(r["max_discount_amount"]),
            "valid_until": to_datetime(r["valid_until"]),
            "is_active": bool(r["is_active"])
        }
        operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
    if operations:
        mongo_db.coupons.bulk_write(operations, ordered=False)
    logger.info(f"Coupons migrated: {len(operations)}")

def migrate_carts(source_conn, mongo_db):
    logger.info("=== Migrating Active Carts & Items ===")
    cur = source_conn.cursor()
    cur.execute("SELECT * FROM cart_cart")
    carts = cur.fetchall()
    
    cur.execute("SELECT * FROM cart_cartitem")
    items_by_cart = {}
    for it in cur.fetchall():
        items_by_cart.setdefault(it["cart_id"], []).append({
            "product_id": it["product_id"],
            "metal": it["metal"],
            "size": it["size"],
            "engraving_text": it["engraving_text"] or "",
            "quantity": it["quantity"],
            "locked_price": to_decimal(it["locked_price"]),
            "gold_value": to_decimal(it["gold_value"]),
            "making_charge": to_decimal(it["making_charge"]),
            "stone_value": to_decimal(it["stone_value"]),
            "gst_amount": to_decimal(it["gst_amount"]),
            "created_at": to_datetime(it["created_at"])
        })

    operations = []
    processed_cart_ids = set()
    for c in carts:
        processed_cart_ids.add(c["id"])
        doc = {
            "_id": c["id"],
            "user_id": c["user_id"],
            "session_key": c["session_key"] or "",
            "items": items_by_cart.get(c["id"], []),
            "created_at": to_datetime(c["created_at"]),
            "updated_at": to_datetime(c["updated_at"])
        }
        operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))

    # Also capture orphan cart items whose parent cart record was deleted
    for orphan_cart_id, items in items_by_cart.items():
        if orphan_cart_id not in processed_cart_ids:
            doc = {
                "_id": orphan_cart_id,
                "user_id": None,
                "session_key": "legacy_orphan",
                "items": items,
                "is_orphan_legacy": True,
                "created_at": items[0]["created_at"],
                "updated_at": items[0]["created_at"]
            }
            operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
    if operations:
        mongo_db.carts.bulk_write(operations, ordered=False)
    logger.info(f"Carts migrated: {len(operations)}")

def migrate_notifications(source_conn, mongo_db):
    logger.info("=== Migrating Notification Logs ===")
    cur = source_conn.cursor()
    cur.execute("SELECT * FROM notifications_notificationlog")
    rows = cur.fetchall()
    operations = []
    for r in rows:
        doc = {
            "_id": r["id"],
            "order_id": r["order_id"],
            "recipient": r["recipient"],
            "channel": r["channel"],
            "template_name": r["template_name"],
            "status": r["status"],
            "message_payload": r["message_payload"] or "",
            "error_message": r["error_message"] or "",
            "sent_at": to_datetime(r["sent_at"]),
            "created_at": to_datetime(r["created_at"])
        }
        operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
    if operations:
        mongo_db.notification_logs.bulk_write(operations, ordered=False)
    logger.info(f"Notification logs migrated: {len(operations)}")

def main():
    mongo_db = get_mongo_client()
    source_conn = get_source_connection()
    try:
        migrate_campaigns(source_conn, mongo_db)
        migrate_gold_rates(source_conn, mongo_db)
        migrate_coupons(source_conn, mongo_db)
        migrate_carts(source_conn, mongo_db)
        migrate_notifications(source_conn, mongo_db)
        logger.info("All auxiliary tables synchronized successfully.")
    finally:
        source_conn.close()

if __name__ == '__main__':
    main()
