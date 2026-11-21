import urllib.request
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

test_ids = [
    # Gold bangles & bracelets
    ('bangles_gold_1', 'https://images.unsplash.com/photo-1617038220319-276d3cfab638?w=800&q=85'),
    ('bangles_gold_2', 'https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800&q=85'),
    ('bangles_gold_3', 'https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=800&q=85'),
    ('bangles_gold_4', 'https://images.unsplash.com/photo-1535632787350-4e68ef0ac584?w=800&q=85'),
    ('bangles_gold_5', 'https://images.unsplash.com/photo-1620656798579-1984d9e87dfa?w=800&q=85'),
    # Earrings
    ('earrings_jhumka_1', 'https://images.unsplash.com/photo-1635767798638-3e25273a8236?w=800&q=85'),
    ('earrings_studs_1', 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&q=85'),
    ('earrings_chandbali_1', 'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&q=85'),
    ('earrings_gold_hoop', 'https://images.unsplash.com/photo-1629224316810-9d8805b95e76?w=800&q=85'),
    ('earrings_trad_1', 'https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?w=800&q=85'),
    # Rings
    ('ring_solitaire', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&q=85'),
    ('ring_cocktail', 'https://images.unsplash.com/photo-1598560917505-59a3ad559071?w=800&q=85'),
    ('ring_gold_band', 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800&q=85'),
]

for name, url in test_ids:
    dest = f"scratch_test_{name}.jpg"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp, open(dest, 'wb') as f:
            f.write(resp.read())
        size = os.path.getsize(dest)
        print(f"SUCCESS: {name:20} -> {size} bytes")
    except Exception as e:
        print(f"FAILED:  {name:20} -> {e}")
