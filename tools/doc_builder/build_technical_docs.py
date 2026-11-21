import os
import sys
from playwright.sync_api import sync_playwright
from assets import get_base64_image, load_qa_results

def build_technical_docs():
    print("Building Technical Documentation HTML...")
    
    img_admin = get_base64_image("browser_snapshots/107_admin_dashboard_orders_appointments.png")

    with open("tools/doc_builder/styles.css", "r", encoding="utf-8") as f:
        css_styles = f.read()

    qa_results = load_qa_results()
    qa_rows_html = ""
    for tc in qa_results:
        qa_rows_html += f"""
        <tr>
          <td><code>{tc['id']}</code></td>
          <td>{tc['scenario']}</td>
          <td><code>{tc['actual']}</code></td>
          <td><span class="badge badge-implemented">{tc['status']}</span></td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Atelier Nilaya — Technical Documentation</title>
  <style>
    {css_styles}
  </style>
</head>
<body>

  <!-- Cover Page -->
  <div class="cover-page">
    <div class="cover-header">
      <div class="cover-crest">✦</div>
      <div class="cover-atelier">ATELIER NILAYA</div>
      <div class="cover-tagline">SURAT, GUJARAT &bull; ESTABLISHED 1954</div>
    </div>

    <div class="cover-center">
      <span class="cover-doc-kicker">Engineering &amp; System Reference</span>
      <h1 class="cover-title">Technical Architecture &amp; Developer Documentation</h1>
      <p class="cover-sub">
        Comprehensive Technical Reference: Dual-Framework Runtime, Database Schema, 
        API Endpoints, Studio Ingestion Scripts, Security Protocols &amp; Deployment Manual.
      </p>

      <div class="cover-meta-grid">
        <div class="cover-meta-item">
          <span class="cover-meta-label">Primary Stack</span>
          <span class="cover-meta-val">Python 3.13 &bull; Django 6.1 &bull; Flask 3.1</span>
        </div>
        <div class="cover-meta-item">
          <span class="cover-meta-label">Database Tier</span>
          <span class="cover-meta-val">SQLite 3 (ACID Embedded Relational)</span>
        </div>
        <div class="cover-meta-item">
          <span class="cover-meta-label">Frontend</span>
          <span class="cover-meta-val">Vanilla ES6+ &bull; HTML5 Canvas &bull; CSS3 Grid</span>
        </div>
        <div class="cover-meta-item">
          <span class="cover-meta-label">Document Version</span>
          <span class="cover-meta-val">Engineering Edition 2.4 (Production)</span>
        </div>
      </div>
    </div>

    <div class="cover-footer">
      <span>Engineering &amp; DevOps Department</span>
      <span>November 2026</span>
    </div>
  </div>

  <!-- Page 2: System Architecture -->
  <h1 class="chapter-title"><span class="chapter-number">Section 1</span>Dual-Framework System Architecture</h1>
  
  <p>
    The Atelier Nilaya platform implements a decoupled, dual-runtime architecture optimized for both editorial prestige 
    and extreme transactional performance:
  </p>

  <div class="callout">
    <span class="callout-title">Architectural Decomposition</span>
    <strong>Django Application (Port 8000):</strong> Orchestrates editorial campaigns, category archives, ORM relationships, 
    PBKDF2 superuser authentication, and the administrative dashboard (<code>/admin/</code>).<br>
    <strong>Flask Application (Port 5000):</strong> Lightweight high-speed micro-storefront managing 360° photographic turntable 
    scrubbing APIs, encrypted session shopping bags, and rapid checkout order placement into SQLite.
  </div>

  <h2>Directory Structure &amp; Key Modules</h2>
  <pre style="background:#fcfbf8; border:1px solid #e0d8ce; padding:10pt; font-family:'JetBrains Mono',monospace; font-size:7.5pt; line-height:1.45; border-radius:4px;">
e:\jewelery/
├── unveiling_atelier/         # Django Project Root
│   ├── settings.py           # Configuration, middleware, template paths
│   ├── urls.py               # Root URLconf routing
│   └── wsgi.py               # WSGI production gateway
├── campaigns/                 # Primary Django Campaign App
│   ├── models.py             # JewelleryCampaign, JewelleryCategory, JewelleryProduct
│   ├── views.py              # HeroAtelierView, CategoryProductListView, ProductDetailView
│   ├── admin.py              # ModelAdmin classes with custom video/poster previews
│   └── urls.py               # Namespaced campaign routing
├── templates/                 # Jinja2 & Django Template System
│   ├── campaigns/            # Django editorial templates (hero.html, detail.html)
│   ├── bag.html              # Dedicated shopping bag page
│   ├── checkout.html         # Delivery details and payment review
│   └── order_confirmed.html   # Instant order receipt ticket
├── static/                    # Static Assets (CSS, JS, Studio Photos, Sketches)
│   ├── products/             # 360° turntable WebP sequences (<slug>/<metal>/spin/)
│   ├── sketches/             # Archival pencil drawing WebPs (1954–1987)
│   └── style.css             # Main stylesheet & responsive layout rules
├── tools/                     # Python Studio Automation Utilities
│   ├── import_images.py      # Batch auto-crop, WebP convert & SQLite metadata ingest
│   ├── render_turntable.py   # Blender bpy 36-frame CAD renderer
│   └── check_assets.py       # Quality assurance asset auditor
├── app.py                     # Flask Micro-Storefront Server
├── nilaya.db                  # Primary Relational SQLite Database (Storefront)
├── db.sqlite3                 # Django Relational Database (CMS & ORM)
└── schema.sql                 # Complete DDL Schema Definition
  </pre>

  <h1 class="chapter-title"><span class="chapter-number">Section 2</span>Database Schema &amp; Relational Entities</h1>
  
  <p>
    The database architecture balances relational integrity with ultra-fast read throughput across 2,044 photographic image records:
  </p>

  <table>
    <thead>
      <tr>
        <th>Table Name</th>
        <th>Database</th>
        <th>Rows</th>
        <th>DDL Constraints &amp; Foreign Keys</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>campaigns_jewellerycampaign</code></td>
        <td>db.sqlite3</td>
        <td>4</td>
        <td><code>id, title, slug (unique), video_desktop, video_mobile, display_order, is_active</code></td>
      </tr>
      <tr>
        <td><code>campaigns_jewellerycategory</code></td>
        <td>db.sqlite3</td>
        <td>7</td>
        <td><code>id, name (unique), slug (unique), subtitle, banner_image, display_order</code></td>
      </tr>
      <tr>
        <td><code>campaigns_jewelleryproduct</code></td>
        <td>db.sqlite3</td>
        <td>43</td>
        <td><code>id, category_id -> campaigns_jewellerycategory, name, sku (unique), price, metal_purity</code></td>
      </tr>
      <tr>
        <td><code>categories</code></td>
        <td>nilaya.db</td>
        <td>7</td>
        <td><code>id, name (unique), slug (unique), description, display_order</code></td>
      </tr>
      <tr>
        <td><code>products</code></td>
        <td>nilaya.db</td>
        <td>16</td>
        <td><code>id, category_id -> categories, name, slug (unique), price, base_metal, approx_weight</code></td>
      </tr>
      <tr>
        <td><code>product_metals</code></td>
        <td>nilaya.db</td>
        <td>64</td>
        <td><code>id, product_id -> products(id) ON DELETE CASCADE, metal, price, in_stock</code></td>
      </tr>
      <tr>
        <td><code>product_images</code></td>
        <td>nilaya.db</td>
        <td>2,044</td>
        <td><code>id, product_id -> products, metal, kind IN ('spin','front','side','top','lifestyle'), frame_index, path</code></td>
      </tr>
      <tr>
        <td><code>orders</code></td>
        <td>nilaya.db</td>
        <td>14</td>
        <td><code>id, customer_name, customer_email, customer_phone, shipping_address, total_amount, status</code></td>
      </tr>
      <tr>
        <td><code>order_items</code></td>
        <td>nilaya.db</td>
        <td>16</td>
        <td><code>id, order_id -> orders(id) ON DELETE CASCADE, product_id -> products, metal, price, quantity</code></td>
      </tr>
      <tr>
        <td><code>designs</code></td>
        <td>nilaya.db</td>
        <td>4</td>
        <td><code>id, product_id -> products(id), year, title, story, sketch_path, sort_order</code></td>
      </tr>
    </tbody>
  </table>

  <h1 class="chapter-title"><span class="chapter-number">Section 3</span>REST API Endpoints &amp; Request Formats</h1>
  
  <table>
    <thead>
      <tr>
        <th>Endpoint Route</th>
        <th>Method</th>
        <th>Runtime</th>
        <th>Payload / Response Format</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>/api/campaigns/</code></td>
        <td>GET</td>
        <td>Django</td>
        <td>Returns active hero carousel items with desktop/mobile video URLs and composition styles.</td>
      </tr>
      <tr>
        <td><code>/api/products/&lt;slug&gt;/images</code></td>
        <td>GET</td>
        <td>Flask</td>
        <td>Returns structured JSON containing spin frame arrays (001–036) and still angles per metal alloy.</td>
      </tr>
      <tr>
        <td><code>/api/cart/</code></td>
        <td>GET / POST / DELETE</td>
        <td>Flask &amp; Django</td>
        <td>Manages session shopping bag items: <code>{{"product_id": 1, "metal": "yellow_gold", "quantity": 1}}</code>.</td>
      </tr>
      <tr>
        <td><code>/api/wishlist/toggle</code></td>
        <td>POST</td>
        <td>Flask &amp; Django</td>
        <td>Toggles product wishlist state: <code>{{"product_id": 1}}</code> -> <code>{{"success": true, "is_wishlisted": true}}</code>.</td>
      </tr>
    </tbody>
  </table>

  <h1 class="chapter-title"><span class="chapter-number">Section 4</span>Studio Photography Ingestion Tools</h1>
  
  <p>
    Located in <code>tools/</code>, these automated scripts process raw studio camera exposures into production-ready WebP files:
  </p>
  <ul>
    <li><code>tools/import_images.py</code>: Takes a directory of raw photos named <code>&lt;slug&gt;__&lt;metal&gt;__&lt;index&gt;.jpg</code>, auto-crops to square, generates 1200px and 600px WebP files (quality 82, &lt;45 KB), and updates <code>product_images</code> table.</li>
    <li><code>tools/check_assets.py</code>: Automated validator confirming that every piece in <code>products</code> has 36 spin frames, 3 stills, and a lifestyle photograph on disk.</li>
  </ul>

  <h1 class="chapter-title"><span class="chapter-number">Section 5</span>Verified Quality Assurance Audit</h1>
  
  <table>
    <thead>
      <tr>
        <th>Test ID</th>
        <th>Test Scenario</th>
        <th>Verified Execution Result</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {qa_rows_html}
    </tbody>
  </table>

  <h1 class="chapter-title"><span class="chapter-number">Section 6</span>Production Deployment &amp; Server Hardening</h1>
  
  <p>
    Recommended production deployment stack on Ubuntu 24.04 LTS:
  </p>
  <ul>
    <li><strong>Application Gateway:</strong> Gunicorn WSGI server running 4 worker processes per core behind Nginx reverse proxy.</li>
    <li><strong>TLS Encryption:</strong> Let's Encrypt automated SSL certificate with HTTP/2 and HSTS enabled.</li>
    <li><strong>Static &amp; Media Serving:</strong> Nginx serves <code>/static/</code> directly with aggressive browser caching headers (<code>Cache-Control: public, max-age=31536000</code>).</li>
    <li><strong>Database Backup Cron:</strong> Nightly automated SQLite snapshot backup using <code>sqlite3 nilaya.db ".backup '/var/backups/nilaya_$(date +%F).db'"</code>.</li>
  </ul>

</body>
</html>"""

    html_path = "Technical Documentation.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    pdf_path = "Technical Documentation.pdf"
    abs_html = os.path.abspath(html_path)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        page.goto(f"file:///{abs_html.replace(os.sep, '/')}", wait_until="networkidle")
        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        browser.close()
    print(f"Generated Technical Documentation.pdf: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

if __name__ == "__main__":
    build_technical_docs()
