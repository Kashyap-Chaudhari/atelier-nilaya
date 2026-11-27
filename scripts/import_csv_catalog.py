import os
import sys
import csv
import shutil
import sqlite3
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unveiling_atelier.settings')

import django
django.setup()

from django.db import transaction
from campaigns.models import JewelleryCategory, JewelleryProduct
from cart.models import CartItem
from orders.models import OrderItem

UPLOADED_CSV = r'C:\Users\hi\.gemini\antigravity\brain\f6fd8ec0-0b1d-46c1-8a61-9162ce04f9f5\.user_uploaded\media_1795591771246_f978c197.csv'
LOCAL_CSV = os.path.join(BASE_DIR, 'data', 'catalog', 'products_265.csv')

if os.path.exists(UPLOADED_CSV):
    os.makedirs(os.path.dirname(LOCAL_CSV), exist_ok=True)
    shutil.copy2(UPLOADED_CSV, LOCAL_CSV)

CSV_PATH = LOCAL_CSV if os.path.exists(LOCAL_CSV) else UPLOADED_CSV

CATEGORY_DEFS = {
    'Necklaces': {
        'slug': 'necklaces',
        'subtitle': 'ROYAL CHOKERS, RANI HAAR & PENDANT NECKLACES',
        'description': 'Handcrafted chokers, ceremonial rani haars, gold chains, custom name necklaces, and delicate pendants cast in 22K & 18K certified gold, platinum, and sterling silver.',
        'banner': '/static/campaigns/img/categories/cat-necklaces.jpg',
        'order': 1,
    },
    'Earrings': {
        'slug': 'earrings',
        'subtitle': 'CHANDBALIS, JHUMKAS, STUDS, HOOPS & DROPS',
        'description': 'Signature Chandbalis, temple bell jhumkas, emerald drops, diamond studs, and everyday minimalist hoops.',
        'banner': '/static/campaigns/img/categories/cat-earrings.jpg',
        'order': 2,
    },
    'Bangles': {
        'slug': 'bangles',
        'subtitle': 'ANTIQUE BANGLES, KADAS, DAILY WEAR & TENNIS BRACELETS',
        'description': 'Heritage gold pair bangles, sculptural Makara and antique kadas, filigree temple wristwear, and bespoke engraved bracelets.',
        'banner': '/static/campaigns/img/categories/cat-bangles.jpg',
        'order': 3,
    },
    'Rings': {
        'slug': 'rings',
        'subtitle': 'SOLITAIRES, COCKTAIL RINGS, WEDDING BANDS & COUPLE RINGS',
        'description': 'Certified diamond engagement solitaires, gemstone cocktail statements, platinum & gold wedding bands, and monogrammed signets.',
        'banner': '/static/campaigns/img/categories/cat-rings.jpg',
        'order': 4,
    },
    'Bridal Jewellery': {
        'slug': 'bridal-jewellery',
        'subtitle': 'COMPLETE BRIDAL SETS, MAANG TIKKA, NATH & TROUSSEAU',
        'description': 'Complete wedding suites in Kundan, Polki, Temple antique gold, and VVS diamond artistry tailored for modern and traditional brides.',
        'banner': '/static/campaigns/img/categories/cat-bridal.jpg',
        'order': 5,
    },
    'Temple Jewellery': {
        'slug': 'temple-jewellery',
        'subtitle': 'TEMPLE PENDANTS, LAKSHMI MOTIFS & SACRED HEIRLOOMS',
        'description': 'Consecrated South Indian temple artistry crafted in 22K antique yellow gold with sacred Lakshmi, peacock, and paisley nakashi.',
        'banner': '/static/campaigns/img/categories/cat-temple.jpg',
        'order': 6,
    },
    'Diamond Jewellery': {
        'slug': 'diamond-jewellery',
        'subtitle': 'CERTIFIED BRACELETS, SOLITAIRE RINGS, PENDANTS & BRIDAL SETS',
        'description': 'Architectural 18K gold and 950 platinum jewellery set with natural, certified high-fire diamonds.',
        'banner': '/static/campaigns/img/categories/cat-diamond.jpg',
        'order': 7,
    },
    "Men's Jewellery": {
        'slug': 'mens-jewellery',
        'subtitle': 'HEAVY KADAS, IMPERIAL CHAINS, SIGNET RINGS, CUFFLINKS & BROOCHES',
        'description': 'Bold sovereign kadas, solid 22K chains, black diamond & onyx signets, gemstone cufflinks, and ceremonial sherwani brooches.',
        'banner': '/static/campaigns/img/menu/promos/promo-mens-jewellery.jpg',
        'order': 8,
    },
}

def resolve_primary_category(menu_groups: str, subcat: str) -> str:
    mg = (menu_groups or '').strip()
    sc = (subcat or '').strip()

    if mg.startswith('Men') or sc in ('Gemstone Cufflinks', 'Gold & Platinum Kadas', 'Imperial Gold Chains', 'Kurta Buttons & Brooches', 'Signet & Solitaire Rings'):
        return "Men's Jewellery"
    if mg.startswith('Bangles') or sc in ('Engraved Bracelets & Kadas',):
        return 'Bangles'
    if mg.startswith('Earrings'):
        return 'Earrings'
    if mg.startswith('Necklaces') or sc in ('Custom Name Necklace', 'Initial Pendants', 'Design Your Own Jewellery'):
        return 'Necklaces'
    if mg.startswith('Rings') or sc in ('Personalised Rings',):
        return 'Rings'
    if mg == 'Bridal' or sc in ('Custom Bridal Sets',):
        return 'Bridal Jewellery'
    if mg == 'Temple':
        return 'Temple Jewellery'
    if mg == 'Diamond':
        return 'Diamond Jewellery'
    return 'Necklaces'

def resolve_metal(tags: str, details: str):
    blob = f"{tags} ; {details}".lower()
    if '950 platinum' in blob or ('platinum' in blob and '18k' not in blob):
        return 'platinum', '950 Platinum'
    if '925 sterling silver' in blob or ('silver' in blob and 'gold' not in blob):
        return 'silver', '925 Sterling Silver'
    if 'rose gold' in blob:
        return 'rose_gold', '18K Rose Gold'
    if 'white gold' in blob:
        return 'platinum', '18K White Gold'
    if '18k (750)' in blob or '18k' in blob:
        return 'yellow_gold', '18K Yellow Gold'
    if 'antique' in blob:
        return 'yellow_gold', '22K Antique Gold'
    return 'yellow_gold', '22K Yellow Gold'

def resolve_gemstones(tags: str, details: str, name: str) -> str:
    blob = f"{tags} ; {details} ; {name}".lower()
    gems = []
    if 'solitaire' in blob:
        gems.append('Certified Solitaire Diamond')
    elif 'diamond' in blob:
        gems.append('Natural Brilliant Diamonds')
    if 'polki' in blob:
        gems.append('Uncut Syndicate Polki')
    if 'kundan' in blob:
        gems.append('Royal Jadau Kundan')
    if 'emerald' in blob:
        gems.append('Zambian / Colombian Emeralds')
    if 'sapphire' in blob:
        gems.append('Natural Sapphire')
    if 'ruby' in blob:
        gems.append('Burmese Ruby')
    if 'pearl' in blob:
        gems.append('Cultured South Sea Pearls')
    if 'onyx' in blob:
        gems.append('Black Onyx')
    if 'navratna' in blob:
        gems.append('Nine Sacred Navratna Gemstones')
    if 'kemp' in blob:
        gems.append('Traditional Kemp Stones')
    if not gems:
        return 'Pure Hallmarked Precious Metal Artistry'
    return ' & '.join(gems)

def verify_existing(paths):
    valid = []
    for p in paths:
        fs_path = os.path.join(BASE_DIR, p.lstrip('/'))
        if os.path.isfile(fs_path):
            valid.append(p)
    return valid

def resolve_matched_image(subcat: str, base_metal: str, name: str, idx_in_sub: int) -> str:
    m = base_metal if base_metal in ('yellow_gold', 'rose_gold', 'platinum', 'silver') else 'yellow_gold'
    sc = (subcat or '').lower()
    nl = (name or '').lower()

    def pimgs(folder, pref_metal):
        order_metals = [pref_metal, 'yellow_gold', 'rose_gold', 'platinum', 'silver']
        seen = set()
        for om in order_metals:
            if om in seen:
                continue
            seen.add(om)
            cands = [f'/static/products/{folder}/{om}/front.webp']
            valid = verify_existing(cands)
            if valid:
                return valid
        return []

    pool = []
    # Match exact upright studio silhouette by subcategory & name (no tilted spin cutouts)
    if 'chandbali' in sc or 'chandbali' in nl:
        pool = ['/static/campaigns/img/menu/promos/promo-chandbalis.jpg'] + pimgs('imperial-chandelier-chandbalis', m)
    elif 'jhumka' in sc or 'jhumka' in nl or 'temple earrings' in sc:
        pool = pimgs('temple-dome-jhumkas-24k-gold', m) + ['/static/campaigns/img/categories/cat-earrings.jpg']
    elif 'drop' in sc or 'drop' in nl or 'dangler' in nl:
        pool = pimgs('emerald-drop-lotus-danglers', m) + ['/static/campaigns/img/categories/cat-earrings.jpg']
    elif 'stud' in sc or 'diamond earrings' in sc or 'hoop' in sc or 'traditional earrings' in sc or 'bridal earrings' in sc:
        pool = pimgs('solitaire-diamond-studs-1-8ct-tw', m) + pimgs('emerald-drop-lotus-danglers', m) + ['/static/campaigns/img/categories/cat-earrings.jpg']
    elif 'choker' in sc or 'choker' in nl or 'bridal necklaces' in sc:
        pool = pimgs('imperial-navratna-choker-suite', m) + ['/static/campaigns/img/menu/promos/promo-royal-chokers.jpg', '/static/campaigns/img/categories/cat-necklaces.jpg']
    elif 'long necklace' in sc or 'haar' in nl or 'mala' in nl:
        pool = pimgs('basra-pearl-emerald-rani-haar', m) + ['/static/campaigns/img/categories/cat-necklaces.jpg']
    elif 'diamond necklace' in sc or 'pendant' in sc or 'custom name necklace' in sc or 'chain' in sc or 'gold necklace' in sc or 'design your own' in sc:
        pool = pimgs('solitaire-diamond-y-drop-necklace', m) + ['/static/campaigns/img/categories/cat-necklaces.jpg', '/static/campaigns/img/menu/promos/promo-diamond-atelier.jpg']
    elif 'temple necklace' in sc or 'temple pendant' in sc:
        pool = pimgs('imperial-navratna-choker-suite', m) + ['/static/campaigns/img/categories/cat-temple.jpg', '/static/campaigns/img/menu/promos/promo-sacred-temple.jpg']
    elif 'cocktail' in sc or 'cocktail' in nl:
        pool = pimgs('pink-sapphire-diamond-cocktail-ring', m) + ['/static/campaigns/img/menu/promos/promo-cocktail-rings.jpg']
    elif 'engagement' in sc or 'diamond rings' in sc or ('solitaire' in nl and 'ring' in nl):
        pool = pimgs('the-empress-cushion-solitaire-2-2ct', m) + ['/static/campaigns/img/menu/promos/promo-solitaire-rings.jpg']
    elif 'wedding band' in sc or 'band' in nl:
        pool = pimgs('eternity-brilliant-diamond-wedding-band', m) + pimgs('dual-tone-platinum-gold-band', m) + ['/static/campaigns/img/categories/cat-rings.jpg']
    elif 'couple' in sc:
        pool = pimgs('dual-tone-platinum-gold-band', m) + pimgs('eternity-brilliant-diamond-wedding-band', m)
    elif 'men’s rings' in sc or "men's rings" in sc or 'signet' in sc or 'personalised rings' in sc or 'gold rings' in sc or 'bridal rings' in sc:
        pool = pimgs('24k-hand-carved-signet-band', m) + pimgs('imperial-navratna-royal-crest-ring', m) + ['/static/campaigns/img/categories/cat-rings.jpg']
    elif 'diamond bracelet' in sc or 'diamond bangle' in sc:
        pool = pimgs('diamond-infinity-tennis-bracelet', m) + ['/static/campaigns/img/categories/cat-diamond.jpg']
    elif 'temple bangle' in sc or 'antique bangle' in sc or 'kada' in sc or 'engraved bracelet' in sc:
        pool = ['/static/campaigns/img/menu/promos/promo-heritage-kadas.jpg', '/static/campaigns/img/categories/cat-bangles.jpg'] + pimgs('imperial-makara-head-kada-22k-gold', m)
    elif 'bangle' in sc:
        pool = ['/static/campaigns/img/categories/cat-bangles.jpg', '/static/campaigns/img/menu/promos/promo-heritage-kadas.jpg'] + pimgs('imperial-makara-head-kada-22k-gold', m)
    elif 'cufflink' in sc or 'brooch' in sc or 'button' in sc:
        pool = ['/static/campaigns/img/menu/promos/promo-mens-jewellery.jpg'] + pimgs('24k-hand-carved-signet-band', m) + pimgs('imperial-navratna-royal-crest-ring', m)
    elif 'temple bridal' in sc:
        pool = ['/static/campaigns/img/categories/cat-temple.jpg', '/static/campaigns/img/menu/promos/promo-sacred-temple.jpg'] + pimgs('imperial-navratna-choker-suite', m)
    elif 'diamond bridal' in sc:
        pool = ['/static/campaigns/img/categories/cat-diamond.jpg', '/static/campaigns/img/menu/promos/promo-diamond-atelier.jpg'] + pimgs('solitaire-diamond-y-drop-necklace', m)
    elif 'bridal' in sc or 'maang tikka' in sc or 'nath' in sc:
        pool = ['/static/campaigns/img/categories/cat-bridal.jpg', '/static/campaigns/img/menu/promos/promo-bridal-edit.jpg'] + pimgs('imperial-navratna-choker-suite', m) + pimgs('basra-pearl-emerald-rani-haar', m)

    pool = verify_existing(pool)
    if not pool:
        pool = verify_existing(['/static/products/the-empress-cushion-solitaire-2-2ct/yellow_gold/front.webp', '/static/campaigns/img/categories/cat-necklaces.jpg'])
    return pool[idx_in_sub % len(pool)]

def main():
    if not os.path.isfile(CSV_PATH):
        print(f"ERROR: CSV file not found at {CSV_PATH}")
        sys.exit(1)

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded {len(rows)} rows from {CSV_PATH}")

    # Track order-referenced product IDs so PROTECT FKs never break
    protected_pids = set(OrderItem.objects.values_list('product_id', flat=True))
    print(f"Historical OrderItem-protected product IDs: {protected_pids}")

    with transaction.atomic():
        # 1. Ensure 8 Categories exist cleanly
        cat_objs = {}
        for cat_name, cdef in CATEGORY_DEFS.items():
            cat, _ = JewelleryCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    'slug': cdef['slug'],
                    'subtitle': cdef['subtitle'],
                    'description': cdef['description'],
                    'banner_url_fallback': cdef['banner'],
                    'display_order': cdef['order'],
                    'is_active': True,
                }
            )
            cat.slug = cdef['slug']
            cat.subtitle = cdef['subtitle']
            cat.description = cdef['description']
            cat.banner_url_fallback = cdef['banner']
            cat.display_order = cdef['order']
            cat.is_active = True
            cat.save()
            cat_objs[cat_name] = cat

        # 2. Delete old products NOT protected by existing orders; archive protected ones unless overwritten
        csv_skus = {r['sku'].strip() for r in rows}
        # Clear cart items pointing to non-CSV/old products to avoid stale items
        CartItem.objects.exclude(product__sku__in=csv_skus).delete()
        deleted_count, _ = JewelleryProduct.objects.exclude(id__in=protected_pids).exclude(sku__in=csv_skus).delete()
        print(f"Removed {deleted_count} old non-order product records.")

        # For any protected products not in CSV, mark archived/out-of-stock
        archived_qs = JewelleryProduct.objects.filter(id__in=protected_pids).exclude(sku__in=csv_skus)
        archived_count = archived_qs.update(is_in_stock=False, is_featured=False, is_bestseller=False, stock_quantity=0)
        print(f"Archived {archived_count} historical order-linked legacy products (is_in_stock=False).")

        # 3. Upsert all 265 CSV products
        sub_counters = {}
        imported_products = []

        for idx, r in enumerate(rows, start=1):
            sku = r['sku'].strip()
            name = r['name'].strip()
            subcat = r['category'].strip()
            menu_groups = r['menu_groups'].strip()
            tags = r['tags'].strip()
            details = r['details'].strip()
            slug = r['slug'].strip()
            price_val = Decimal(str(r['price_inr']).strip())

            sub_counters[subcat] = sub_counters.get(subcat, 0)
            idx_in_sub = sub_counters[subcat]
            sub_counters[subcat] += 1

            primary_cat_name = resolve_primary_category(menu_groups, subcat)
            cat_obj = cat_objs[primary_cat_name]

            base_metal, metal_purity = resolve_metal(tags, details)
            gemstones = resolve_gemstones(tags, details, name)
            matched_img = resolve_matched_image(subcat, base_metal, name, idx_in_sub)

            weight_str = (r.get('gold_or_metal_weight_g') or '').strip()
            stone_str = (r.get('stone_value_inr') or '').strip()
            making_str = (r.get('making_pct') or '').strip()

            weight = Decimal(weight_str) if weight_str else Decimal('10.000')
            stone_val = Decimal(stone_str) if stone_str else Decimal('0.00')
            making_pct = Decimal(making_str) if making_str else Decimal('14.00')

            tags_combined = f"{tags}; MenuGroups: {menu_groups}; Subcategory: {subcat}" if tags else f"MenuGroups: {menu_groups}; Subcategory: {subcat}"
            is_best = ('bestsellers' in tags.lower())
            is_feat = ('new arrivals' in tags.lower() or 'featured' in tags.lower() or idx_in_sub == 0)

            short_desc = f"{details}. Handcrafted in {metal_purity} — {subcat}."
            full_desc = (
                f"{name} ({subcat}). {details}. Certified hallmarked fine jewellery piece crafted for {primary_cat_name}. "
                f"Gemstone & Material Note: {gemstones}."
            )

            existing = JewelleryProduct.objects.filter(sku=sku).first() or JewelleryProduct.objects.filter(slug=slug).first()
            if existing:
                prod = existing
            else:
                prod = JewelleryProduct()

            prod.category = cat_obj
            prod.subcategory = subcat
            prod.tags = tags_combined
            prod.name = name
            prod.slug = slug
            prod.sku = sku
            prod.eyebrow = f"{subcat} • {metal_purity}"
            prod.short_description = short_desc[:300]
            prod.description = full_desc
            prod.price = price_val
            prod.metal_purity = metal_purity
            prod.gemstone_details = gemstones[:200]
            prod.image = None
            prod.image_url_fallback = matched_img
            prod.is_featured = is_feat
            prod.is_bestseller = is_best
            prod.is_in_stock = True
            prod.stock_quantity = 5
            prod.display_order = idx
            prod.base_metal = base_metal
            prod.gold_weight_grams = weight
            prod.making_charge_type = 'percentage'
            prod.making_charge_value = making_pct
            prod.stone_value = stone_val
            prod.save()

            imported_products.append(prod)

    print(f"\nSuccessfully imported {len(imported_products)} products into Django SQLite!")
    print(f"Total active (is_in_stock=True) products in SQLite: {JewelleryProduct.objects.filter(is_in_stock=True).count()}")

    # 4. Sync MongoDB (nilaya_atelier.products & jewelery_shop.products)
    try:
        from pymongo import MongoClient
        from bson.decimal128 import Decimal128
        import datetime

        mclient = MongoClient('mongodb://127.0.0.1:27017', serverSelectionTimeoutMS=2500)
        # 4a. nilaya_atelier.products
        ndb = mclient['nilaya_atelier']
        ndb.products.delete_many({})
        ndocs = []
        for p in imported_products:
            ndocs.append({
                '_id': p.id,
                'sku': p.sku,
                'name': p.name,
                'slug': p.slug,
                'category': {
                    'id': p.category.id,
                    'name': p.category.name,
                    'slug': p.category.slug,
                },
                'subcategory': p.subcategory,
                'tags': p.tags,
                'eyebrow': p.eyebrow,
                'short_description': p.short_description,
                'description': p.description,
                'media': {'primary_image': p.image_url_fallback},
                'pricing': {
                    'price_inr': float(p.price),
                    'base_metal': p.base_metal,
                    'metal_purity': p.metal_purity,
                    'gold_weight_grams': Decimal128(str(p.gold_weight_grams)),
                    'making_charge_type': p.making_charge_type,
                    'making_charge_value': Decimal128(str(p.making_charge_value)),
                    'stone_value': Decimal128(str(p.stone_value)),
                    'advance_payment_percentage': Decimal128('25'),
                },
                'specifications': {
                    'gemstone_details': p.gemstone_details,
                    'huid_number': p.huid_number or '',
                    'available_sizes': [s.strip() for s in p.available_sizes.split(',') if s.strip()],
                },
                'inventory': {
                    'stock_quantity': p.stock_quantity,
                    'is_in_stock': True,
                    'is_one_of_a_kind': p.is_one_of_a_kind,
                    'is_made_to_order': p.is_made_to_order,
                    'making_days': p.making_days,
                },
                'flags': {
                    'is_featured': p.is_featured,
                    'is_bestseller': p.is_bestseller,
                    'is_active': True,
                },
                'created_at': datetime.datetime.now(datetime.timezone.utc),
            })
        if ndocs:
            ndb.products.insert_many(ndocs)
        print(f"Synced {len(ndocs)} products to MongoDB 'nilaya_atelier.products'.")

        # 4b. jewelery_shop.products (Node/Mongoose schema: price in paise)
        jdb = mclient['jewelery_shop']
        jdb.products.delete_many({})
        jdocs = []
        now = datetime.datetime.now(datetime.timezone.utc)
        for p in imported_products:
            jdocs.append({
                'name': p.name,
                'slug': p.slug,
                'description': p.description,
                'price': int(round(float(p.price) * 100)), # integer paise
                'images': [p.image_url_fallback],
                'category': p.category.name.lower(),
                'subcategory': p.subcategory,
                'material': p.metal_purity,
                'stock': p.stock_quantity,
                'isActive': True,
                'createdAt': now,
                'updatedAt': now,
            })
        if jdocs:
            jdb.products.insert_many(jdocs)
        print(f"Synced {len(jdocs)} products to MongoDB 'jewelery_shop.products'.")
    except Exception as e:
        print(f"WARNING: MongoDB sync skipped/failed: {e}")

    # 5. Sync nilaya.db (products table & feature_tiles 4 showcase products)
    nilaya_db_path = os.path.join(BASE_DIR, 'nilaya.db')
    if os.path.exists(nilaya_db_path):
        try:
            conn = sqlite3.connect(nilaya_db_path)
            cur = conn.cursor()
            cur.execute("DELETE FROM products")
            cat_slug_to_id = {}
            for row in cur.execute("SELECT id, slug FROM categories").fetchall():
                cat_slug_to_id[row[1]] = row[0]

            showcase_by_cat = {}
            for p in imported_products:
                ncat_id = cat_slug_to_id.get(p.category.slug, 1)
                if 'ring' in p.category.slug:
                    mtype = 'ring'
                elif 'ear' in p.category.slug:
                    mtype = 'earrings'
                elif 'neck' in p.category.slug:
                    mtype = 'necklace'
                else:
                    mtype = 'bangle'

                if p.category.slug in ('rings', 'necklaces', 'earrings', 'bangles') and p.is_featured and p.category.slug not in showcase_by_cat:
                    showcase_by_cat[p.category.slug] = str(p.id)

                cur.execute("""
                    INSERT INTO products (
                        id, category_id, name, slug, price, base_metal, purity,
                        approx_weight, stone, certificate, description, model_type,
                        image_fallback, is_featured, gold_weight_grams,
                        making_charge_type, making_charge_value, stone_value,
                        collection_name, metal_type, primary_image, gold_purity, is_best_seller, stock_qty
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p.id, ncat_id, p.name, p.slug, float(p.price), p.base_metal, p.metal_purity,
                    f"{p.gold_weight_grams} g", p.gemstone_details, 'BIS 916 HUID / IGI Certified',
                    p.description, mtype, p.image_url_fallback, 1 if p.is_featured else 0,
                    float(p.gold_weight_grams), p.making_charge_type, float(p.making_charge_value),
                    float(p.stone_value), p.subcategory, p.metal_purity, p.image_url_fallback,
                    p.metal_purity, 1 if p.is_bestseller else 0, p.stock_quantity
                ))

            # Update homepage featured tile to showcase 4 diverse featured products
            feat_ids = [showcase_by_cat[k] for k in ('rings', 'necklaces', 'earrings', 'bangles') if k in showcase_by_cat]
            if len(feat_ids) < 4:
                feat_ids = [str(p.id) for p in imported_products if p.is_featured][:4]
            if feat_ids:
                cur.execute("UPDATE feature_tiles SET product_ids = ? WHERE kind = 'product_group'", (','.join(feat_ids),))
            conn.commit()
            conn.close()
            print(f"Synced {len(imported_products)} products to nilaya.db (featured tile IDs: {feat_ids}).")
        except Exception as e:
            print(f"WARNING: nilaya.db sync error: {e}")

if __name__ == '__main__':
    main()
