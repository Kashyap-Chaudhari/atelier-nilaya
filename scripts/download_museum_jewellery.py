import os
import urllib.request
from PIL import Image

headers = {'User-Agent': 'AaranyaJewelleryMaster/1.0 (contact@aaranya.atelier)'}

assets = [
    ('bangles_916', 'https://upload.wikimedia.org/wikipedia/commons/d/db/916_Bangles.jpg'),
    ('bangle_big_kada', 'https://upload.wikimedia.org/wikipedia/commons/e/e9/A_big_bangle_one.JPG'),
    ('bangles_four', 'https://upload.wikimedia.org/wikipedia/commons/c/cd/4_bangles.JPG'),
    ('bangle_arm_bracelet', 'https://upload.wikimedia.org/wikipedia/commons/c/c2/Arm_bracelet%2C_India%2C_1800s_AD%2C_gold%2C_pearls%2C_ruby_-_Dallas_Museum_of_Art_-_DSC04947.jpg'),
    ('bangle_doris_duke', 'https://upload.wikimedia.org/wikipedia/commons/8/8b/Bracelet_from_India%2C_Doris_Duke_Foundation_for_Islamic_Art_accession_57.74.JPG'),
    ('earrings_kammalu', 'https://upload.wikimedia.org/wikipedia/commons/a/ad/2_kammalu.JPG'),
    ('earrings_delhi', 'https://upload.wikimedia.org/wikipedia/commons/b/b0/Ear_ornaments_from_Delhi%2C_Doris_Duke_Foundation_for_Islamic_Art_accession_57.59.JPG'),
    ('earrings_madras', 'https://upload.wikimedia.org/wikipedia/commons/d/dd/Ear_pendant%2C_circa_1885_CE%2C_Madras%2C_housed_in_the_V%26A_Museum%2C_London.jpg'),
]

for name, url in assets:
    dest = f"scratch_wiki_{name}.jpg"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp, open(dest, 'wb') as f:
            f.write(resp.read())
        size = os.path.getsize(dest)
        im = Image.open(dest)
        print(f"SUCCESS: {name:20} -> {size} bytes, size={im.size}")
    except Exception as e:
        print(f"FAILED:  {name:20} -> {e}")
