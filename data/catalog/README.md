# Atelier Nilaya catalogue pack

| File | What it is |
|---|---|
| `catalog.json` | Everything: meta, 176 collections, 1,149 products (use this for import) |
| `products.csv` | Same products as a flat sheet (opens in Excel) |
| `collections.json` | Your menu subcategories with the product count of each |
| `rates.json` | Today's gold, silver, platinum and stone rates plus their sources |
| `build_catalog.py` | Recalculates every price from `rates.json`. Run `python build_catalog.py` |
| `check_media.py` | Verifies photos and marks only complete products as published |

## How prices are calculated
`price = (net weight x metal rate + making charge % + stone value) + 3% GST`, rounded to the nearest Rs 10.
Metal rates are the published rates for 20 Nov 2026 (Gandhinagar, Gujarat). To refresh: edit the numbers in
`rates.json`, then run `python build_catalog.py`. Every price updates.

## What is real and what is an estimate
* REAL: metal rates, GST, purity, the structure of your menu, naming style used in the Indian jewellery market.
* ESTIMATE: net weight, making %, and stone values. They are market-typical, not your actual stock.
  Replace them with the real figures from each piece's tag or invoice before you publish it.
* Stone rates are estimates for natural stones. Platinum quotes vary widely between dealers: confirm yours.
* Bestsellers, Customer Favourites and Trending are left EMPTY on purpose. Fill them from real order data.
  New Arrivals / Latest Collections are seeded with the last 5 products of each family. Change in admin.
* Items marked `price.type = starting_from` are made-to-order (personalised / bespoke). Price is a starting point.

## Photos and 360 views (you must shoot these)
No product is published until it has its photos. Per product (`media` in catalog.json):
* `front`, `side`, `detail` (close-up with hallmark), `model` (worn): WebP, long edge at least 1600 px.
* `360/frame_01.webp ... frame_36.webp`: 36 photos, one every 10 degrees on a turntable, same camera height,
  same lighting, plain seamless background. The 360 viewer needs real frames; it cannot be generated from one photo.
* Folder layout: `media/products/<SKU>/front.webp` ... and `media/products/<SKU>/360/frame_01.webp`.
* Do NOT reuse one photo for different products. `check_media.py` flags duplicates.
Run `python check_media.py --media ./media` then import `catalog.published.json` (only ready products are published).

## Importing into your project
Map fields to your models: `sku`, `name`, `slug`, `metal.label`, `metal.purity`, `net_weight_g`,
`making_charge_pct`, `price.total_inr`, `price.metal_value`, `price.making_charge`, `price.stone_value`,
`stones[]`, `menus[]` (collection slugs; a product can sit in many), `styles`, `occasions`, `made_to_order`,
`personalisation`, `media.*`, `published`. In the store, always recalculate price on the server from your admin's
daily gold rate, never from this file.
