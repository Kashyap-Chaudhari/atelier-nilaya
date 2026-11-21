import os
import sys
from playwright.sync_api import sync_playwright
from assets import get_base64_image

def build_features_summary():
    print("Building Website Features Summary HTML...")
    
    img_hero = get_base64_image("browser_snapshots/01_desktop_hero_aaranya.png")
    img_turntable = get_base64_image("browser_snapshots/44_category_photographic_spin_desktop.png")
    img_sketchbook = get_base64_image("browser_snapshots/61_sketchbook_initial_35pct.png")
    img_featured = get_base64_image("browser_snapshots/100_django_featured_edit_desktop.png")
    img_family = get_base64_image("browser_snapshots/django_family_desktop_1280.png")
    img_bag = get_base64_image("browser_snapshots/201_bag_step1_drawer.png")

    with open("tools/doc_builder/styles.css", "r", encoding="utf-8") as f:
        css_styles = f.read()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Atelier Nilaya — Website Features Summary</title>
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
      <span class="cover-doc-kicker">Executive Client Presentation</span>
      <h1 class="cover-title">Website Features Summary</h1>
      <p class="cover-sub">
        High-Level Overview of the Digital Flagship Architecture, Customer Touchpoints, 
        360° Turntable System &amp; Commercial Capabilities.
      </p>

      <div class="cover-meta-grid">
        <div class="cover-meta-item">
          <span class="cover-meta-label">Document Role</span>
          <span class="cover-meta-val">Executive Business Summary</span>
        </div>
        <div class="cover-meta-item">
          <span class="cover-meta-label">Client</span>
          <span class="cover-meta-val">Atelier Nilaya Stakeholders</span>
        </div>
        <div class="cover-meta-item">
          <span class="cover-meta-label">Version</span>
          <span class="cover-meta-val">Executive Edition 2.4</span>
        </div>
        <div class="cover-meta-item">
          <span class="cover-meta-label">Date</span>
          <span class="cover-meta-val">November 2026</span>
        </div>
      </div>
    </div>

    <div class="cover-footer">
      <span>Atelier Nilaya Fine Jewellery Platform</span>
      <span>Surat &bull; Gujarat &bull; India</span>
    </div>
  </div>

  <!-- Page 2: Executive Overview -->
  <h1 class="chapter-title"><span class="chapter-number">Executive Brief</span>Platform Value &amp; Feature Highlights</h1>
  
  <p>
    The Atelier Nilaya digital flagship is engineered to deliver the prestige, confidence, and bespoke hospitality 
    of a high-jewellery private salon directly to luxury consumers across India and worldwide. 
    Below is a summary of the core feature pillars powering the platform:
  </p>

  <div class="callout">
    <span class="callout-title">Four Foundational Pillars</span>
    <strong>1. Authentic Photographic Turntables:</strong> Zero dark procedural 3D meshes; pure studio photography.<br>
    <strong>2. Generational Archival Storytelling:</strong> Digitized 1954–1987 founder sketches with interactive comparison.<br>
    <strong>3. Trust-Centered Family Moments:</strong> Milestone-based customer stories replacing generic star ratings.<br>
    <strong>4. Dual-Runtime High Performance:</strong> Python Django + Flask delivering sub-second page loads on all devices.
  </div>

  <h2>1. Cinematic Hero &amp; Curatorial Story Rail</h2>
  <p>
    Welcomes high-net-worth visitors with an immersive campaign video stage (Zone B), an interactive vertical story rail 
    (Zone A) highlighting masterwork collections, and a dynamic next-collection preview (Zone C).
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_hero}" class="screenshot-img" alt="Hero Experience">
    </div>
    <span class="screenshot-caption"><strong>Figure 1:</strong> Full-Screen Cinematic Campaign Video Stage with Synchronized Vertical Story Rail.</span>
  </div>

  <h2>2. Studio Photographic 360° Turntable System</h2>
  <p>
    Enables clients to scrub around rings, necklaces, and bangles in 360 degrees. Preloads only the hero frame initially 
    for fast mobile performance, dynamically switching metal alloys (22K Gold, Rose Gold, Platinum) with live price updates.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_turntable}" class="screenshot-img" alt="360 Turntable">
    </div>
    <span class="screenshot-caption"><strong>Figure 2:</strong> 360-Degree Turntable Product Catalogue with Multi-Metal Alloy Swatching.</span>
  </div>

  <h2>3. The Archival Sketchbook: From Pencil to Jewel</h2>
  <p>
    An interactive before-and-after slider comparing the founder's original hand-drawn pencil sketches (1954–1987) against 
    the finished photographic jewel, establishing undeniable atelier heritage.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_sketchbook}" class="screenshot-img" alt="The Sketchbook">
    </div>
    <span class="screenshot-caption"><strong>Figure 3:</strong> The Sketchbook: Interactive Pencil-to-Jewel Archival Comparison Slider.</span>
  </div>

  <h2>4. "Pieces that Found Their Family" &amp; Heirloom Certificate</h2>
  <p>
    Combines verified customer milestone stories (weddings, anniversaries, first grandchildren) with an accordion FAQ answering 
    BIS hallmarks, buyback, insured armored courier, and concludes with a physical Heirloom Certificate card.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_family}" class="screenshot-img" alt="Family Album">
    </div>
    <span class="screenshot-caption"><strong>Figure 4:</strong> "Pieces that Found Their Family" (Milestone Album, Bench FAQ &amp; Heirloom Certificate).</span>
  </div>

  <h2>5. Complete Shopping Bag &amp; Checkout Flow</h2>
  <p>
    Features a slide-in shopping bag drawer, a dedicated bag summary table with metal weights, and a streamlined 
    delivery details checkout that commits verified orders directly into the database.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_bag}" class="screenshot-img" alt="Shopping Bag Drawer">
    </div>
    <span class="screenshot-caption"><strong>Figure 5:</strong> Slide-in Shopping Bag Drawer with Itemized Metal &amp; Gemstone Breakdown.</span>
  </div>

  <h2>Feature Matrix &amp; Implementation Status</h2>
  <table>
    <thead>
      <tr>
        <th>Feature Category</th>
        <th>Capabilities Delivered</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Header &amp; Navigation</strong></td>
        <td>Announcement bar, brand logo, search bar, wishlist counter, 8-category mega menus.</td>
        <td><span class="badge badge-implemented">Implemented</span></td>
      </tr>
      <tr>
        <td><strong>Homepage Storytelling</strong></td>
        <td>Video stage, story rail, velvet tray, manifesto, featured edit, sketchbook, family album.</td>
        <td><span class="badge badge-implemented">Implemented</span></td>
      </tr>
      <tr>
        <td><strong>Catalogue &amp; 360° Spin</strong></td>
        <td>360-degree turntable viewer, 3 still angles, lifestyle worn photo, metal alloy swatching.</td>
        <td><span class="badge badge-implemented">Implemented</span></td>
      </tr>
      <tr>
        <td><strong>Shopping Bag &amp; Checkout</strong></td>
        <td>Bag drawer, /bag page, transparent making charges, /checkout form, database order creation.</td>
        <td><span class="badge badge-implemented">Implemented</span></td>
      </tr>
      <tr>
        <td><strong>Private Salon Bookings</strong></td>
        <td>Two-step modal for Surat showroom appointment or encrypted video consultation.</td>
        <td><span class="badge badge-implemented">Implemented</span></td>
      </tr>
      <tr>
        <td><strong>Administrative CMS</strong></td>
        <td>Django /admin/ managing campaigns, video uploads, categories, products, and order logs.</td>
        <td><span class="badge badge-implemented">Implemented</span></td>
      </tr>
      <tr>
        <td><strong>Payment Gateway (Live API)</strong></td>
        <td>Simulated checkout active; modular endpoint ready for Razorpay/Stripe live API credentials.</td>
        <td><span class="badge badge-partial">Ready for Credentials</span></td>
      </tr>
      <tr>
        <td><strong>Courier API (Live Tracking)</strong></td>
        <td>Insured transit workflow documented; webhook integration planned for Phase 2.</td>
        <td><span class="badge badge-planned">Planned Phase 2</span></td>
      </tr>
    </tbody>
  </table>

</body>
</html>"""

    html_path = "Website Features Summary.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    pdf_path = "Website Features Summary.pdf"
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
    print(f"Generated Website Features Summary.pdf: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

if __name__ == "__main__":
    build_features_summary()
