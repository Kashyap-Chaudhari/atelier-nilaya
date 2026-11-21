import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

pages = [
    ('bangles_stack', 'https://unsplash.com/photos/a-stack-of-ornate-gold-bangles-on-a-dark-surface-f51775896add'),
    ('bangles_rows', 'https://unsplash.com/photos/rows-of-ornate-gold-bangles-with-intricate-designs-78e8244290d3'),
    ('bangles_charcoal', 'https://unsplash.com/photos/gold-bangle-on-charcoal-pieces-zayed_ahmed_zadu'),
]

for name, page_url in pages:
    try:
        req = urllib.request.Request(page_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
            # Look for images.unsplash.com/photo-...
            matches = re.findall(r'https://images\.unsplash\.com/photo-[a-zA-Z0-9\-_]+', html)
            if matches:
                img_url = matches[0] + '?w=800&q=85'
                print(f"FOUND: {name} -> {img_url}")
                img_req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(img_req, timeout=10) as img_resp, open(f'scratch_{name}.jpg', 'wb') as f:
                    f.write(img_resp.read())
                print(f"DOWNLOADED {name} successfully!")
    except Exception as e:
        print(f"FAILED {name}: {e}")
