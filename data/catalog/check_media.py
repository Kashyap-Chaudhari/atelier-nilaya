#!/usr/bin/env python3
"""Checks that every product has its real photos, then marks only complete products as published.
Usage:  python check_media.py --media ./media
Expected files per product (see catalog.json -> media):
  products/<SKU>/front.webp, side.webp, detail.webp, model.webp
  products/<SKU>/360/frame_01.webp ... frame_36.webp
Writes: catalog.published.json (only ready products have published=true) and media_report.csv
Rules enforced: all files present, long edge >= 1600 px (if Pillow is installed), and no image
reused by two different products (catches wrong-photo-on-wrong-product mistakes).
"""
import argparse, csv, hashlib, json, os, collections
ap = argparse.ArgumentParser(); ap.add_argument("--media", default="./media"); ap.add_argument("--catalog", default="catalog.json"); a = ap.parse_args()
try:
    from PIL import Image
except ImportError:
    Image = None
cat = json.load(open(a.catalog, encoding="utf-8"))
owner, report, ready = {}, [], 0
for p in cat["products"]:
    m, issues = p["media"], []
    files = [m["front"], m["side"], m["detail"], m["model"]] + [f'{m["view360"]["folder"]}/' + m["view360"]["pattern"].format(n=i) for i in range(1, m["view360"]["frames"] + 1)]
    for f in files:
        path = os.path.join(a.media, f)
        if not os.path.isfile(path): issues.append("missing " + f); continue
        h = hashlib.md5(open(path, "rb").read()).hexdigest()
        if h in owner and owner[h] != p["sku"]: issues.append(f"duplicate of {owner[h]}: {f}")
        owner.setdefault(h, p["sku"])
        if Image:
            try:
                w, hh = Image.open(path).size
                if max(w, hh) < 1600: issues.append(f"too small ({w}x{hh}): {f}")
            except Exception:
                issues.append("unreadable " + f)
    p["published"] = not issues
    p["status"] = "ready" if not issues else "needs_photos"
    ready += not issues
    report.append([p["sku"], p["name"], p["status"], len(issues), "; ".join(issues[:5])])
json.dump(cat, open("catalog.published.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open("media_report.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh); w.writerow(["sku", "name", "status", "issue_count", "first_issues"]); w.writerows(report)
print(f"{ready} of {len(cat['products'])} products are ready to publish. See media_report.csv")
