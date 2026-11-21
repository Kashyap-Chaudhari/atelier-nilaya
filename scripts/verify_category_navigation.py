import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unveiling_atelier.settings')
django.setup()

from django.test import Client
from campaigns.models import JewelleryCategory, JewelleryProduct

c = Client()

print("=" * 60)
print("AARANYA — CATEGORY & MEGA MENU ROUTE VERIFICATION")
print("=" * 60)

categories = list(JewelleryCategory.objects.all())
print(f"Total Categories in DB: {len(categories)}")
for cat in categories:
    url = f"/category/{cat.slug}/"
    resp = c.get(url)
    prod_count = cat.products.filter(is_in_stock=True).count()
    print(f"[{resp.status_code}] {cat.name:20} -> {url:30} ({prod_count} artworks)")
    assert resp.status_code == 200, f"Failed {url}"

print("\n--- Subcategory & Query Filter Tests ---")
test_filters = [
    ("/category/earrings/?sub=jhumka", "Jhumkas"),
    ("/category/earrings/?sub=chandbali", "Chandbalis"),
    ("/category/earrings/?sub=stud", "Studs"),
    ("/category/rings/?sub=engagement", "Engagement Rings"),
    ("/category/rings/?sub=cocktail", "Cocktail Rings"),
    ("/category/bangles/?sub=kada", "Heritage Kadas"),
    ("/category/bangles/?metal=gold", "Gold Bangles"),
    ("/category/bridal-jewellery/?sub=necklace", "Bridal Necklaces"),
    ("/category/temple-jewellery/?sub=lakshmi", "Lakshmi Motifs"),
    ("/category/diamond-jewellery/?sub=solitaire", "Diamond Solitaires"),
    ("/vault/", "Complete Vault"),
    ("/vault/?filter=new", "Vault New"),
    ("/vault/?filter=bestseller", "Vault Bestsellers"),
]

for url, label in test_filters:
    resp = c.get(url)
    # Check that HTML rendered successfully
    assert resp.status_code == 200, f"Failed {url}"
    has_artworks = b'aaranya-product-card' in resp.content
    print(f"[{resp.status_code}] {label:25} -> {url:45} (Contains artworks: {has_artworks})")

print("\n" + "=" * 60)
print("ALL ROUTES VERIFIED SUCCESSFULLY! ZERO BROKEN LINKS.")
print("=" * 60)
