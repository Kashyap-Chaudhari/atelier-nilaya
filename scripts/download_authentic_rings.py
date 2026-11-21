import urllib.request
import os

headers = {'User-Agent': 'AaranyaJewelleryMaster/1.0'}

ring_urls = [
    ('mughal_ring', 'https://upload.wikimedia.org/wikipedia/commons/3/3a/Archer%27s_ring_from_India%2C_Mughal_period%2C_18th_century%2C_white_jade%2C_gold%2C_rubies%2C_emeralds_and_diamonds%2C_HAA.JPG'),
    ('gold_wedding_bands', 'https://images.unsplash.com/photo-1590548784585-643d2b9f2925?w=800&q=85'),
    ('gold_signet_ring', 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&q=85'),
    ('cocktail_cluster_ring', 'https://images.unsplash.com/photo-1608042314453-ae338d80c427?w=800&q=85'),
    ('diamond_band_ring', 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&q=85')
]

for name, url in ring_urls:
    dest = f"scratch_ring_{name}.jpg"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp, open(dest, 'wb') as f:
            f.write(resp.read())
        print(f"SUCCESS: {name} -> {os.path.getsize(dest)} bytes")
    except Exception as e:
        print(f"FAILED:  {name} -> {e}")
