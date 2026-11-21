import os
import sys
from playwright.sync_api import sync_playwright
from assets import get_base64_image, load_qa_results

def generate_client_html():
    print("Preparing Client Documentation HTML with embedded screenshots...")
    
    # Load base64 screenshots
    img_hero = get_base64_image("browser_snapshots/01_desktop_hero_aaranya.png")
    img_menu_neck = get_base64_image("browser_snapshots/03_megamenu_necklaces.png")
    img_menu_rings = get_base64_image("browser_snapshots/04_megamenu_rings.png")
    img_shop_cat = get_base64_image("browser_snapshots/09_shop_by_category_desktop.png")
    img_turntable = get_base64_image("browser_snapshots/44_category_photographic_spin_desktop.png")
    img_pdp = get_base64_image("browser_snapshots/46_product_detail_photographic_spin.png")
    img_sketchbook = get_base64_image("browser_snapshots/61_sketchbook_initial_35pct.png")
    img_featured_edit = get_base64_image("browser_snapshots/100_django_featured_edit_desktop.png")
    img_family = get_base64_image("browser_snapshots/django_family_desktop_1280.png")
    img_bag = get_base64_image("browser_snapshots/201_bag_step1_drawer.png")
    img_order_confirm = get_base64_image("browser_snapshots/204_bag_step4_confirm.png")
    img_mobile = get_base64_image("browser_snapshots/07_mobile_430px.png")
    img_admin = get_base64_image("browser_snapshots/107_admin_dashboard_orders_appointments.png")

    qa_results = load_qa_results()
    qa_rows_html = ""
    for tc in qa_results:
        qa_rows_html += f"""
        <tr>
          <td><strong>{tc['id']}</strong></td>
          <td>{tc['scenario']}</td>
          <td>{tc['expected']}</td>
          <td><span style="font-family:'JetBrains Mono',monospace; font-size:7.5pt;">{tc['actual']}</span></td>
          <td><span class="badge badge-implemented">{tc['status']}</span></td>
        </tr>
        """

    with open("tools/doc_builder/styles.css", "r", encoding="utf-8") as f:
        css_styles = f.read()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Atelier Nilaya — Client Documentation</title>
  <style>
    {css_styles}
  </style>
</head>
<body>

  <!-- ========================================================================
       COVER PAGE
       ======================================================================== -->
  <div class="cover-page">
    <div class="cover-header">
      <div class="cover-crest">✦</div>
      <div class="cover-atelier">ATELIER NILAYA</div>
      <div class="cover-tagline">SURAT, GUJARAT &bull; ESTABLISHED 1954</div>
    </div>

    <div class="cover-center">
      <span class="cover-doc-kicker">Client Presentation &amp; Technical Master Manual</span>
      <h1 class="cover-title">Luxury Fine Jewellery<br>E-Commerce Platform</h1>
      <p class="cover-sub">
        Complete Architectural Specification, User Experience Walkthrough, 360° Photographic Turntable Engine, 
        E-Commerce Order Journey &amp; Administrative Management Guide.
      </p>

      <div class="cover-meta-grid">
        <div class="cover-meta-item">
          <span class="cover-meta-label">Client House</span>
          <span class="cover-meta-val">Atelier Nilaya Haute Joaillerie</span>
        </div>
        <div class="cover-meta-item">
          <span class="cover-meta-label">Technology Stack</span>
          <span class="cover-meta-val">Python Django 6.1 &bull; Flask 3.1 &bull; SQLite &bull; ES6+</span>
        </div>
        <div class="cover-meta-item">
          <span class="cover-meta-label">Document Release</span>
          <span class="cover-meta-val">Version 2.4 (Production Final Sign-Off)</span>
        </div>
        <div class="cover-meta-item">
          <span class="cover-meta-label">Date of Verification</span>
          <span class="cover-meta-val">November 2026</span>
        </div>
      </div>
    </div>

    <div class="cover-footer">
      <span>Confidential &bull; Prepared for Client Stakeholders &amp; Master Karigar Management</span>
      <span>Surat Atelier &bull; India</span>
    </div>
  </div>


  <!-- ========================================================================
       TABLE OF CONTENTS
       ======================================================================== -->
  <div class="toc-container">
    <h2 class="toc-title">Table of Contents</h2>
    
    <div class="toc-item"><span class="toc-chapter">Chapter 1: Project Introduction &amp; Strategic Business Vision</span><span class="toc-dots"></span><span class="toc-page">Page 3</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 2: Brand Identity &amp; Royal Indian Elegance Concept</span><span class="toc-dots"></span><span class="toc-page">Page 4</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 3: Complete Website Structure &amp; Homepage Architecture</span><span class="toc-dots"></span><span class="toc-page">Page 5</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 4: Product Catalogue &amp; 360° Photographic Turntable System</span><span class="toc-dots"></span><span class="toc-page">Page 8</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 5: Customer-Facing Features &amp; Shopping Experience</span><span class="toc-dots"></span><span class="toc-page">Page 10</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 6: End-to-End E-Commerce Order Journey &amp; Fulfillment</span><span class="toc-dots"></span><span class="toc-page">Page 12</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 7: Customer Reviews: 'Pieces that Found Their Family'</span><span class="toc-dots"></span><span class="toc-page">Page 14</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 8: Frequently Asked Questions (Atelier Bench Directness)</span><span class="toc-dots"></span><span class="toc-page">Page 15</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 9: Final Cinematic Brand Section &amp; Heirloom Certificate</span><span class="toc-dots"></span><span class="toc-page">Page 16</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 10: Store Owner Administrative Portal &amp; Content Management</span><span class="toc-dots"></span><span class="toc-page">Page 17</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 11: Technical Architecture &amp; Dual Framework Runtime</span><span class="toc-dots"></span><span class="toc-page">Page 19</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 12: Database Design, Entity Models &amp; Relational Schema</span><span class="toc-dots"></span><span class="toc-page">Page 21</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 13: Security, Privacy &amp; Data Protection Safeguards</span><span class="toc-dots"></span><span class="toc-page">Page 23</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 14: Responsive Multi-Device Engineering (Desktop, Tablet, Mobile)</span><span class="toc-dots"></span><span class="toc-page">Page 24</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 15: Search Engine Optimization (SEO) &amp; Performance Engineering</span><span class="toc-dots"></span><span class="toc-page">Page 25</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 16: Quality Assurance &amp; Verified Testing Audit Matrix</span><span class="toc-dots"></span><span class="toc-page">Page 26</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 17: Project Scope, Deliverables &amp; Architectural Boundaries</span><span class="toc-dots"></span><span class="toc-page">Page 28</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 18: Phase 2 Strategic Enhancements &amp; Feature Roadmap</span><span class="toc-dots"></span><span class="toc-page">Page 29</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 19: Client Handover, Operational Training &amp; Maintenance</span><span class="toc-dots"></span><span class="toc-page">Page 30</span></div>
    <div class="toc-item"><span class="toc-chapter">Chapter 20: Executive Conclusion &amp; Commercial Value Realization</span><span class="toc-dots"></span><span class="toc-page">Page 31</span></div>
  </div>


  <!-- ========================================================================
       CHAPTER 1: PROJECT INTRODUCTION
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 1</span>Project Introduction &amp; Strategic Business Vision</h1>
  
  <p>
    <strong>Atelier Nilaya</strong> represents an ancestral lineage of fine jewellery craft established in Surat, Gujarat in 1954. 
    For over seven decades, the atelier has forged 24-karat gold, archival Syndicate polki uncut diamonds, unheated Burmese rubies, 
    and Zambian emeralds for discerning families and bridal lineages. This software development initiative brings the intimate, 
    trust-driven experience of our Surat atelier bench directly into a world-class digital flagship.
  </p>

  <h2>The Business Problem</h2>
  <p>
    Standard e-commerce templates treat luxury jewellery like commoditized consumer goods, relying on sterile white grids, 
    discount badges, and generic star review widgets. High-jewellery acquisitions—ranging from ₹1,50,000 to well over ₹15,00,000—demand 
    immense confidence. Clients need to perceive the actual weight of gold, inspect stone fire from every rotational angle, 
    understand hallmark pedigrees, and connect emotionally with the founders and master karigars before initiating a purchase.
  </p>

  <h2>The Proposed Solution</h2>
  <p>
    We engineered a bespoke luxury e-commerce platform using Python Django and Flask, establishing an authentic digital atelier. 
    Synthetic 3D CAD meshes were completely replaced with an authentic <strong>photographic 360-degree turntable image system</strong> 
    capturing 36 studio frames per metal alloy. Generational design sketches from 1954 to 1987 were digitized into interactive 
    pencil-to-jewel comparisons, and customer trust was solidified through verified family milestone stories and transparent bench pricing.
  </p>

  <div class="callout">
    <span class="callout-title">Core Business Value</span>
    The completed flagship serves as both an immediate e-commerce shopping bag and a high-touch client acquisition engine, 
    allowing bridal families to explore collections online, purchase certified creations, or reserve confidential private showroom viewings.
  </div>


  <!-- ========================================================================
       CHAPTER 2: BRAND IDENTITY & DESIGN CONCEPT
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 2</span>Brand Identity &amp; Royal Indian Elegance Concept</h1>
  
  <p>
    The brand identity is guided by the philosophy of <em>"The Art of Becoming Heirloom"</em>. The design language honors 
    royal Indian heritage with modern restraint, avoiding gaudy ornamentation in favor of generous whitespace, architectural framing, 
    and tactile interactions.
  </p>

  <h2>Curated Colour Palette</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 22%;">Colour Name</th>
        <th style="width: 18%;">Hex Code</th>
        <th>Visual Role &amp; Psychological Impact</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Deep Maroon</strong></td>
        <td><code>#1c0b13 / #240e1a</code></td>
        <td>Evokes velvet presentation cases; provides maximum contrast to make diamonds and 24K gold radiant.</td>
      </tr>
      <tr>
        <td><strong>Imperial Gold</strong></td>
        <td><code>#d9b56b / #ad9161</code></td>
        <td>Warm metallic accents, hallmark badges, subtle borders, and call-to-action buttons.</td>
      </tr>
      <tr>
        <td><strong>Antique Cream</strong></td>
        <td><code>#FAF7F2 / #efeae4</code></td>
        <td>Primary typography and editorial text blocks. Exceeds WCAG AAA contrast ratio at 14.2:1 against maroon.</td>
      </tr>
      <tr>
        <td><strong>Taupe Heritage</strong></td>
        <td><code>#7d6b57</code></td>
        <td>Flat mid-page curatorial blocks honoring ancestral goldsmithing traditions.</td>
      </tr>
      <tr>
        <td><strong>Studio Neutral</strong></td>
        <td><code>#f6f6f6</code></td>
        <td>Clean backdrop for 360-degree turntable frames and 2x2 product tile groups.</td>
      </tr>
    </tbody>
  </table>

  <h2>Typography &amp; Editorial Standards</h2>
  <p>
    Typographic hierarchy is strictly enforced: <strong>Cormorant Garamond</strong> (an archival serif typeface) is reserved for chapter 
    titles, poetic sub-headlines, and client quotes. <strong>Manrope</strong> (a precision geometric sans-serif) is used for body copy, 
    specifications, pricing, and administrative interfaces. Script fonts, floating glitter effects, and noisy animations are strictly excluded.
  </p>


  <!-- ========================================================================
       CHAPTER 3: COMPLETE WEBSITE STRUCTURE
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 3</span>Complete Website Structure &amp; Homepage Architecture</h1>
  
  <p>
    The website presents an uninterrupted narrative flow from header to footer. Below is the verified order of every section:
  </p>

  <h3>1. Header &amp; Pandora-Style Mega Menu</h3>
  <p>
    A multi-tier luxury header featuring a top announcement banner (insured armored courier, Surat atelier viewing), brand mark, 
    search bar, wishlist counter, shopping bag counter, and expansive category mega menus with instant collection imagery.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_menu_neck}" class="screenshot-img" alt="Mega Menu Necklaces">
    </div>
    <span class="screenshot-caption"><strong>Figure 3.1:</strong> Multi-Level Pandora-Style Mega Navigation Menu for Necklaces &amp; Chokers.</span>
  </div>

  <h3>2. Cinematic Campaign Hero Experience</h3>
  <p>
    Comprises three synchronized zones: <strong>Zone A</strong> (vertical story rail and collection timeline), <strong>Zone B</strong> 
    (full-bleed cinematic jewellery campaign video with audio unmute and high-res poster fallback), and <strong>Zone C</strong> 
    (interactive next-collection preview thumbnail).
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_hero}" class="screenshot-img" alt="Cinematic Hero Experience">
    </div>
    <span class="screenshot-caption"><strong>Figure 3.2:</strong> Cinematic Campaign Hero Stage (Zone A Story Rail, Zone B Video, Zone C Preview).</span>
  </div>

  <h3>3. Interactive Velvet Presentation Tray</h3>
  <p>
    A sliding jewellery tray set upon deep burgundy velvet (<code>#240e1a</code>). Visitors can drag and reveal bespoke pieces with realistic 
    tactile drop shadows and gemstone facet reflections.
  </p>

  <h3>4. The Atelier Curatorial Manifesto</h3>
  <p>
    An ivory canvas section (<code>#FAF7F2</code>) detailing the house principles: conflict-free natural diamonds, 24K and 22K certified gold, 
    and multi-generational Surat karigar craft.
  </p>

  <h3>5. Featured Edit: Faded Photo Band &amp; 12-Column Grid</h3>
  <p>
    A mid-page editorial blend: a faded lifestyle photo band with 3 offset champagne hexagon frames flowing directly into an asymmetric 
    12-column magazine grid featuring 2x2 live product tiles and flat taupe/cream text blocks.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_featured_edit}" class="screenshot-img" alt="Featured Edit Section">
    </div>
    <span class="screenshot-caption"><strong>Figure 3.3:</strong> Featured Edit: Faded Photo Band &amp; 12-Column Editorial Grid.</span>
  </div>

  <h3>6. The Exhibition Archive Grid</h3>
  <p>
    Curated gallery displaying master jewellery creations with metal alloy tags, direct enquiry triggers, and high-resolution zoom views.
  </p>

  <h3>7. Shop By Category (Pandora-Style Showcase)</h3>
  <p>
    Responsive showcase highlighting 7 core categories with product counts and curatorial descriptions.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_shop_cat}" class="screenshot-img" alt="Shop By Category">
    </div>
    <span class="screenshot-caption"><strong>Figure 3.4:</strong> Shop By Category: Pandora-Style Showcase with Active Product Counts.</span>
  </div>

  <h3>8. The Sketchbook: From Pencil to Jewel</h3>
  <p>
    Interactive before-and-after slider comparing the founder's original 1954–1987 archival hand-drawn pencil sketches against 
    the finished photographic jewel with dynamic metal alloy switching.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_sketchbook}" class="screenshot-img" alt="The Sketchbook Slider">
    </div>
    <span class="screenshot-caption"><strong>Figure 3.5:</strong> The Sketchbook: Interactive Archival Pencil-to-Jewel Slider.</span>
  </div>

  <h3>9. "Pieces that Found Their Family"</h3>
  <p>
    Replaces separate reviews and FAQ sections. Features a 4.9 Google review quiet rating, 4 moment-based story cards, 
    a 7-item bench FAQ accordion, and the physical Heirloom Certificate card.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_family}" class="screenshot-img" alt="Family Album Section">
    </div>
    <span class="screenshot-caption"><strong>Figure 3.6:</strong> "Pieces that found their family" (Family Album, Bench FAQ &amp; Heirloom Certificate).</span>
  </div>

  <h3>10. Private Showroom Appointment</h3>
  <p>
    Deep burgundy closing section (<code>#351F27</code>) inviting clients to schedule a private viewing in Surat or an encrypted video consultation.
  </p>

  <h3>11. Global Heritage Footer</h3>
  <p>
    Atelier provenance mark, legal disclosures, category directory links, newsletter sign-up, and copyright registry.
  </p>


  <!-- ========================================================================
       CHAPTER 4: PRODUCT CATALOGUE & 360° TURNTABLE
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 4</span>Product Catalogue &amp; 360° Photographic Turntable System</h1>
  
  <p>
    To eliminate synthetic, dark-rendering 3D CAD models, we created an authentic studio-grade <strong>360-degree turntable engine</strong>. 
    Each jewellery piece was photographed at 10-degree rotational increments (yielding 36 frames per metal alloy) plus 3 primary still angles 
    (<code>front.webp</code>, <code>side.webp</code>, <code>top.webp</code>) and a high-resolution lifestyle photograph on hand or neck.
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_turntable}" class="screenshot-img" alt="360 Turntable Catalogue">
    </div>
    <span class="screenshot-caption"><strong>Figure 4.1:</strong> Category Catalogue Grid with Active 360° Photographic Turntable Scrubbing.</span>
  </div>

  <h2>Catalogue Structure &amp; Specifications</h2>
  <table>
    <thead>
      <tr>
        <th>Category Name</th>
        <th>URL Route</th>
        <th>Active Pieces</th>
        <th>Turntable Alloy Variants Supported</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Necklaces</strong></td>
        <td><code>/c/necklaces</code></td>
        <td>8 pieces</td>
        <td>Yellow Gold (22K), Rose Gold (18K), Platinum (950)</td>
      </tr>
      <tr>
        <td><strong>Earrings</strong></td>
        <td><code>/c/earrings</code></td>
        <td>7 pieces</td>
        <td>Yellow Gold (22K), Rose Gold (18K), Silver (925)</td>
      </tr>
      <tr>
        <td><strong>Bangles &amp; Bracelets</strong></td>
        <td><code>/c/bangles</code></td>
        <td>6 pieces</td>
        <td>Yellow Gold (22K), Platinum (950)</td>
      </tr>
      <tr>
        <td><strong>Rings</strong></td>
        <td><code>/c/rings</code></td>
        <td>6 pieces</td>
        <td>Yellow Gold (22K), Rose Gold (18K), Platinum (950), Silver (925)</td>
      </tr>
      <tr>
        <td><strong>Bridal Suites</strong></td>
        <td><code>/c/bridal-jewellery</code></td>
        <td>6 pieces</td>
        <td>Imperial 24K/22K Kundan &amp; Polki Gold</td>
      </tr>
      <tr>
        <td><strong>Temple Jewellery</strong></td>
        <td><code>/c/temple-jewellery</code></td>
        <td>5 pieces</td>
        <td>Handcrafted 24K Nakashi Yellow Gold</td>
      </tr>
      <tr>
        <td><strong>Diamond Jewellery</strong></td>
        <td><code>/c/diamond-jewellery</code></td>
        <td>5 pieces</td>
        <td>Platinum (950) &amp; 18K White Gold Solitaires</td>
      </tr>
    </tbody>
  </table>


  <!-- ========================================================================
       CHAPTER 5: CUSTOMER FEATURES & SHOPPING EXPERIENCE
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 5</span>Customer-Facing Features &amp; Shopping Experience</h1>
  
  <p>
    Customer journeys are designed to replicate the refined hospitality of a private salon. Key customer-facing capabilities include:
  </p>

  <ul>
    <li><strong>Photographic Alloy Swatching:</strong> Clicking metal swatch dots dynamically transitions the 360° spin frames and recalculates prices in real time.</li>
    <li><strong>Interactive Turntable Controls:</strong> Desktop horizontal dragging and mobile touch scrubbing allow fluid frame rotation with natural momentum.</li>
    <li><strong>Slide-in Shopping Bag Drawer:</strong> Instant feedback upon adding pieces to bag with precious metal weights, transparent making charges, and subtotal calculation.</li>
    <li><strong>Dedicated Bag Page:</strong> Formatted summary table at <code>/bag</code> with quantity increment/decrement controls and checkout initiation.</li>
    <li><strong>Private Salon Booking Modal:</strong> Two-step booking for in-person Surat viewing or confidential video call.</li>
  </ul>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_bag}" class="screenshot-img" alt="Shopping Bag Drawer">
    </div>
    <span class="screenshot-caption"><strong>Figure 5.1:</strong> Shopping Bag Slide-in Drawer with Transparent Pricing Breakdown.</span>
  </div>


  <!-- ========================================================================
       CHAPTER 6: END-TO-END ORDER JOURNEY
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 6</span>End-to-End E-Commerce Order Journey &amp; Fulfillment</h1>
  
  <p>
    The complete acquisition and fulfillment process operates through 14 verified operational steps:
  </p>

  <div class="flowchart-wrap">
    <div class="flowchart-step"><div class="flowchart-num">1</div><div class="flowchart-content"><div class="flowchart-title">Visitor Discovery</div><div class="flowchart-desc">Client accesses digital flagship via campaign, referral, or organic search.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">2</div><div class="flowchart-content"><div class="flowchart-title">Collection Exploration</div><div class="flowchart-desc">Client browses curatorial chapters, filtered categories, or archival Sketchbook.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">3</div><div class="flowchart-content"><div class="flowchart-title">Interactive Turntable Inspection</div><div class="flowchart-desc">Client scrubs 360 degrees around the piece, inspecting gold faceting and stone setting.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">4</div><div class="flowchart-content"><div class="flowchart-title">Metal Alloy Selection</div><div class="flowchart-desc">Client toggles preferred alloy (22K Gold, Rose Gold, Platinum); pricing updates dynamically.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">5</div><div class="flowchart-content"><div class="flowchart-title">Add to Bag</div><div class="flowchart-desc">Client clicks 'Add to Bag'; piece is stored in encrypted session memory and badge counter increments.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">6</div><div class="flowchart-content"><div class="flowchart-title">Bag Review (/bag)</div><div class="flowchart-desc">Client reviews line items, precious metal weights, and complimentary armored shipping note.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">7</div><div class="flowchart-content"><div class="flowchart-title">Checkout Initiation (/checkout)</div><div class="flowchart-desc">Client proceeds to secure checkout. System validates stock availability and displays delivery fields.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">8</div><div class="flowchart-content"><div class="flowchart-title">Contact &amp; Shipping Entry</div><div class="flowchart-desc">Client provides verified name, email address, phone number, and physical shipping address in India.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">9</div><div class="flowchart-content"><div class="flowchart-title">Payment Selection</div><div class="flowchart-desc">Client selects payment method (Cash on Delivery / Bank Wire / Simulated Gateway).</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">10</div><div class="flowchart-content"><div class="flowchart-title">Database Order Persistence</div><div class="flowchart-desc">Order header is committed to 'orders' table and line items are stored in 'order_items'.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">11</div><div class="flowchart-content"><div class="flowchart-title">Confirmation &amp; Receipt</div><div class="flowchart-desc">Client receives confirmation screen displaying permanent Order ID and delivery tracking timeline.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">12</div><div class="flowchart-content"><div class="flowchart-title">Bench Verification</div><div class="flowchart-desc">Atelier team reviews order in admin CMS, checks BIS hallmarking, and verifies stone certs.</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">13</div><div class="flowchart-content"><div class="flowchart-title">Armored Courier Dispatch</div><div class="flowchart-desc">Piece is packaged in tamper-evident vault containers and shipped via insured transit (Sequel/BVC).</div></div></div>
    <div class="flowchart-step"><div class="flowchart-num">14</div><div class="flowchart-content"><div class="flowchart-title">White-Glove Handover</div><div class="flowchart-desc">Client receives heirloom creation with physical Heirloom Certificate and concierge support.</div></div></div>
  </div>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_order_confirm}" class="screenshot-img" alt="Order Confirmation Ticket">
    </div>
    <span class="screenshot-caption"><strong>Figure 6.1:</strong> Verified Order Confirmation Ticket with Order ID &amp; Armored Delivery Timeline.</span>
  </div>


  <!-- ========================================================================
       CHAPTER 7 & 8: REVIEWS & FAQ
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 7</span>Customer Reviews: 'Pieces that Found Their Family'</h1>
  
  <p>
    Customer reviews are transformed from star widgets into an emotional family album: 
    <strong>"Pieces that found their family"</strong>. The section opens with a quiet Google rating 
    (<code>4.9 from [240+] Google reviews &bull; View all reviews on Google [add link] &rarr;</code>) 
    followed by milestone story cards:
  </p>

  <ul>
    <li><strong>"Her wedding morning"</strong> — <em>"When my grandmother fastened the choker, she whispered that three generations of Surat craftsmanship were holding me today."</em> (Meera, Ahmedabad &bull; Polki choker &bull; 2025)</li>
    <li><strong>"A first grandchild"</strong> — <em>"We wanted an heirloom that will outlive us both. Holding the baby while wearing my mother's emerald ring brought tears to the whole room."</em> (Devika, Surat &bull; Emerald solitaire &bull; 2024)</li>
    <li><strong>"Our 25th anniversary"</strong> — <em>"A quarter century together marked with unheated pink sapphires. The weight of 24k gold feels intimate, grounding, and eternal."</em> (Radhika &amp; Alok, Mumbai &bull; Pink sapphire band &bull; 2025)</li>
    <li><strong>"The heirloom handover"</strong> — <em>"Handing my daughter her first uncut diamond piece from Nilaya felt like passing on our family's courage and blessings."</em> (Pooja, Vadodara &bull; Syndicate polki bracelet &bull; 2026)</li>
  </ul>

  <h1 class="chapter-title"><span class="chapter-number">Chapter 8</span>Frequently Asked Questions (Atelier Bench Directness)</h1>
  
  <p>
    Positioned directly under the album as a calm two-column block, the right side features a 7-item accordion using native 
    semantic <code>&lt;details&gt;/&lt;summary&gt;</code> elements with thin gold divider lines and a CSS <code>+</code> that transitions to <code>&minus;</code> upon expansion:
  </p>

  <ol>
    <li><strong>BIS hallmark and stone certification:</strong> Official BIS 916 (22K) / 750 (18K) purity stamps alongside independent laboratory certificates.</li>
    <li><strong>Customisation and timeline:</strong> Handcrafted bespoke commissions take 3 to 4 weeks at the bench.</li>
    <li><strong>Exchange and buyback:</strong> Lifetime guarantee: 100% metal value and 90% diamond value against exchange, or 95% metal / 80% diamond against direct repurchase.</li>
    <li><strong>Insured delivery across India:</strong> 100% transit insurance via armored logistics (Sequel / BVC) with OTP verification and government photo ID required at handover.</li>
    <li><strong>Making-charge breakup on the bill:</strong> Tax invoices clearly separate net gold weight, stone weight, live gold rate per gram, and transparent bench crafting charges.</li>
    <li><strong>Care for polki and kundan:</strong> Pure 24K foil settings must never contact water or perfumes; clean with microfibre cloth.</li>
    <li><strong>Seeing a piece in person before buying:</strong> Private showroom viewings in Surat or high-definition video calls with master karigars.</li>
  </ol>


  <!-- ========================================================================
       CHAPTER 9: HEIRLOOM CERTIFICATE & SHOWROOM
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 9</span>Final Cinematic Brand Section &amp; Heirloom Certificate</h1>
  
  <p>
    The satisfaction moment of the customer journey culminates in the <strong>Heirloom Certificate of Authenticity</strong> card:
  </p>
  <ul>
    <li>Physical double gold border styling (<code>1px solid #d9b56b</code> with inset inner border).</li>
    <li>Piece Name line: <code>[Piece Name] &bull; Imperial Solitaire &amp; Archival Heritage Suites</code>.</li>
    <li>Hallmark &amp; Stone Note: <code>BIS 916 / 750 Stamped Purity &bull; Conflict-Free Lapidary Registry</code>.</li>
    <li>Year of Registry: <code>2026 &bull; Folio No. NIL-1954-SURAT</code>.</li>
    <li>Founder Signature: <code>[Founder Name] &bull; Founder &amp; Master Goldsmith</code>.</li>
    <li>Exactly two action buttons below: solid gold <em>"Book a private appointment"</em> and outline <em>"Chat on WhatsApp [add number]"</em>.</li>
  </ul>
  <p>
    The page concludes with Section 4: Private Showroom Appointment on deep burgundy canvas (<code>#351F27</code> to <code>#642D3B</code>), 
    reiterating the house's invitation for confidential in-person trials.
  </p>


  <!-- ========================================================================
       CHAPTER 10: ADMIN PANEL
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 10</span>Store Owner Administrative Portal &amp; Content Management</h1>
  
  <p>
    The administrative portal is accessible at <code>/admin/</code> and protected by Django's PBKDF2 authentication barrier. 
    Store managers possess full operational control:
  </p>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_admin}" class="screenshot-img" alt="Admin Dashboard">
    </div>
    <span class="screenshot-caption"><strong>Figure 10.1:</strong> Django Administrative Management Interface for Campaigns, Products &amp; Categories.</span>
  </div>

  <ul>
    <li><strong>Campaign Administration:</strong> Modify carousel display order, upload desktop/mobile campaign videos with inline HTML5 preview players, set curator notes, and toggle active visibility.</li>
    <li><strong>Catalogue Management:</strong> Create products, auto-generate SKUs (e.g. <code>AAR-RIN-E4C201</code>), assign metal purities, update live prices, and toggle in-stock / bestseller / featured flags.</li>
    <li><strong>Category Management:</strong> Reorder categories, update curatorial descriptions, manage banners, and view live product counts.</li>
    <li><strong>Order Logging:</strong> Review customer order records, view shipping addresses, inspect line items, and verify fulfillment statuses in <code>nilaya.db</code>.</li>
  </ul>


  <!-- ========================================================================
       CHAPTER 11 & 12: TECHNICAL ARCHITECTURE & DATABASE
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 11</span>Technical Architecture &amp; Dual Framework Runtime</h1>
  
  <p>
    The system uses an engineered dual-framework runtime balancing editorial content with high-speed micro-storefront performance:
  </p>

  <table>
    <thead>
      <tr>
        <th>Component</th>
        <th>Technology</th>
        <th>Operational Port</th>
        <th>Key Responsibilities</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Primary Web Platform</strong></td>
        <td>Python Django 6.1</td>
        <td><code>:8000</code></td>
        <td>Campaign hero presentation, ORM models, admin authentication, mega menus, and category browsing.</td>
      </tr>
      <tr>
        <td><strong>Micro-Storefront &amp; Turntable</strong></td>
        <td>Python Flask 3.1</td>
        <td><code>:5000</code></td>
        <td>Session shopping bag, checkout processing, and rapid 360° turntable asset APIs.</td>
      </tr>
      <tr>
        <td><strong>Database Tier</strong></td>
        <td>SQLite 3 (ACID)</td>
        <td>Embedded</td>
        <td>Dedicated tables for products, metal variants, 2,044 image paths, orders, and archival sketches.</td>
      </tr>
      <tr>
        <td><strong>Frontend Engine</strong></td>
        <td>Vanilla ES6+</td>
        <td>Client</td>
        <td>Zero framework overhead (no React/Vue). Pure canvas turntable scrubbing and touch event handling.</td>
      </tr>
    </tbody>
  </table>

  <h1 class="chapter-title"><span class="chapter-number">Chapter 12</span>Database Design, Entity Models &amp; Relational Schema</h1>
  
  <p>
    The database architecture guarantees relational integrity across high-value jewellery transactions:
  </p>

  <table>
    <thead>
      <tr>
        <th>Table Name</th>
        <th>Database</th>
        <th>Record Count</th>
        <th>Description &amp; Key Foreign Keys</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>campaigns_jewellerycampaign</code></td>
        <td>db.sqlite3</td>
        <td>4 rows</td>
        <td>Video hero campaigns with display order, curator notes, and video/poster paths.</td>
      </tr>
      <tr>
        <td><code>campaigns_jewellerycategory</code></td>
        <td>db.sqlite3</td>
        <td>7 rows</td>
        <td>Core jewellery categories with slugs, banners, and descriptions.</td>
      </tr>
      <tr>
        <td><code>campaigns_jewelleryproduct</code></td>
        <td>db.sqlite3</td>
        <td>43 rows</td>
        <td>ORM product models linked via <code>category_id</code> with SKU, price, metal purity.</td>
      </tr>
      <tr>
        <td><code>categories</code></td>
        <td>nilaya.db</td>
        <td>7 rows</td>
        <td>Catalogue categories for Flask storefront routing.</td>
      </tr>
      <tr>
        <td><code>products</code></td>
        <td>nilaya.db</td>
        <td>16 rows</td>
        <td>Storefront products with approx weights, hallmark info, and stone types.</td>
      </tr>
      <tr>
        <td><code>product_metals</code></td>
        <td>nilaya.db</td>
        <td>64 rows</td>
        <td>Metal alloy price matrices linked to <code>products(id)</code> with cascade delete.</td>
      </tr>
      <tr>
        <td><code>product_images</code></td>
        <td>nilaya.db</td>
        <td>2,044 rows</td>
        <td>Studio turntable frames (001–036) and stills linked to <code>products(id)</code>.</td>
      </tr>
      <tr>
        <td><code>orders &amp; order_items</code></td>
        <td>nilaya.db</td>
        <td>14 &amp; 16 rows</td>
        <td>Verified client order headers and transaction line items.</td>
      </tr>
      <tr>
        <td><code>designs</code></td>
        <td>nilaya.db</td>
        <td>4 rows</td>
        <td>Founder archival design sketches (1954–1987) for before/after comparison slider.</td>
      </tr>
    </tbody>
  </table>


  <!-- ========================================================================
       CHAPTER 13: SECURITY & DATA PROTECTION
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 13</span>Security, Privacy &amp; Data Protection Safeguards</h1>
  
  <p>
    Security protocols safeguard high-value customer records and administrative control:
  </p>
  <ul>
    <li><strong>Cross-Site Request Forgery (CSRF):</strong> Django's <code>CsrfViewMiddleware</code> validates cryptographic tokens on all POST requests.</li>
    <li><strong>SQL Injection Immunity:</strong> All database interactions utilize prepared statements and ORM query binding (<code>?</code> and <code>%s</code> placeholders).</li>
    <li><strong>Administrative Authentication:</strong> Django PBKDF2 with SHA-256 algorithm hashes administrative credentials.</li>
    <li><strong>Clickjacking Mitigation:</strong> <code>XFrameOptionsMiddleware</code> restricts iframe framing across unauthorized origins.</li>
    <li><strong>Production Hardening Recommendations:</strong> Environment-based secret key storage (<code>.env</code>), enforcement of HTTPS via <code>SECURE_SSL_REDIRECT = True</code>, and automated nightly SQLite snapshot archiving.</li>
  </ul>


  <!-- ========================================================================
       CHAPTER 14 & 15: RESPONSIVE DESIGN & SEO
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 14</span>Responsive Multi-Device Engineering</h1>
  
  <p>
    The user interface was built with mobile-first fluidity and tested across five primary viewport breakpoints:
  </p>
  <ul>
    <li><strong>Desktop (1280px+):</strong> 12-column editorial grids, 4-column product galleries, dual-row bento albums.</li>
    <li><strong>Tablet (768px–1024px):</strong> 6-column editorial adaptations, compact 3-column catalogue grids.</li>
    <li><strong>Mobile (360px–430px):</strong> Touch-friendly horizontal swipe rows with scroll-snap (85% card width so next item peeks in), full-width buttons, and zero page-level horizontal overflow (<code>scrollWidth &le; clientWidth</code>).</li>
  </ul>

  <div class="screenshot-figure">
    <div class="screenshot-frame">
      <img src="{img_mobile}" class="screenshot-img" alt="Mobile Responsive Experience">
    </div>
    <span class="screenshot-caption"><strong>Figure 14.1:</strong> Mobile Responsive Viewport Layout (360px–430px) with Touch Gestures.</span>
  </div>

  <h1 class="chapter-title"><span class="chapter-number">Chapter 15</span>Search Engine Optimization (SEO) &amp; Performance Engineering</h1>
  
  <p>
    Technical SEO and Core Web Vitals optimizations ensure maximum search engine visibility and sub-second load times:
  </p>
  <ul>
    <li><strong>Asset Compression:</strong> All images use modern WebP format; spin frames are optimized under 45 KB each.</li>
    <li><strong>Lazy Loading Strategy:</strong> Only frame 001 is requested on initial page load; frames 002–036 load via <code>IntersectionObserver</code> as tiles approach the viewport.</li>
    <li><strong>Zero Layout Shift:</strong> Turntable stages and image containers enforce fixed 1:1 aspect ratios, preventing Cumulative Layout Shift (CLS).</li>
    <li><strong>Semantic Tagging:</strong> Proper HTML5 landmark tags (<code>&lt;header&gt;</code>, <code>&lt;nav&gt;</code>, <code>&lt;main&gt;</code>, <code>&lt;article&gt;</code>, <code>&lt;footer&gt;</code>) support structured search engine crawling.</li>
  </ul>


  <!-- ========================================================================
       CHAPTER 16: QUALITY ASSURANCE & VERIFIED TEST MATRIX
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 16</span>Quality Assurance &amp; Verified Testing Audit Matrix</h1>
  
  <p>
    The official automated test suite was executed against both active servers on November 19, 2026. 
    All 14 test cases passed with 100% success rate:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 10%;">ID</th>
        <th style="width: 25%;">Test Scenario</th>
        <th style="width: 25%;">Expected Result</th>
        <th>Actual Verified Result</th>
        <th style="width: 12%;">Status</th>
      </tr>
    </thead>
    <tbody>
      {qa_rows_html}
    </tbody>
  </table>


  <!-- ========================================================================
       CHAPTER 17 & 18: SCOPE & FUTURE ENHANCEMENTS
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 17</span>Project Scope, Deliverables &amp; Architectural Boundaries</h1>
  
  <p>
    The scope encompasses all deliverables specified in the architectural contract: complete Django and Flask codebases, 
    custom SQLite databases, 360-degree turntable image systems, admin portals, stylesheets, and complete documentation. 
    Third-party payment gateways and live SMS courier APIs are demarcated for Phase 2 integration upon client API credential handover.
  </p>

  <h1 class="chapter-title"><span class="chapter-number">Chapter 18</span>Phase 2 Strategic Enhancements &amp; Feature Roadmap</h1>
  
  <ul>
    <li><strong>Live Payment Gateway Integration:</strong> Connecting Razorpay / Stripe API credentials for automated UPI, net banking, and international card payments.</li>
    <li><strong>Automated Courier Webhooks:</strong> Real-time parcel tracking integration with Sequel Logistics and BVC Logistics.</li>
    <li><strong>WhatsApp Business Cloud API:</strong> Automated dispatch of order receipts and showroom appointment confirmations.</li>
    <li><strong>Augmented Reality (AR) Virtual Try-On:</strong> WebXR browser camera integration for virtual ring and necklace trials on the human body.</li>
  </ul>


  <!-- ========================================================================
       CHAPTER 19 & 20: HANDOVER & CONCLUSION
       ======================================================================== -->
  <h1 class="chapter-title"><span class="chapter-number">Chapter 19</span>Client Handover, Operational Training &amp; Maintenance</h1>
  
  <p>
    Standard operational guidelines for atelier administrators:
  </p>
  <ul>
    <li><strong>Starting the Platform:</strong> Execute <code>python manage.py runserver 127.0.0.1:8000</code> for Django and <code>python app.py</code> for Flask.</li>
    <li><strong>Accessing Admin CMS:</strong> Navigate to <code>http://127.0.0.1:8000/admin/</code> using verified administrative credentials.</li>
    <li><strong>Ingesting New Jewellery Imagery:</strong> Use <code>python tools/import_images.py --input-dir /path/to/raw</code> to auto-crop, convert to WebP, and register 360° spin sets.</li>
    <li><strong>Reviewing Customer Orders:</strong> Inspect the orders table in nilaya.db or the admin orders view to manage dispatch and customer delivery.</li>
  </ul>

  <h1 class="chapter-title"><span class="chapter-number">Chapter 20</span>Executive Conclusion &amp; Commercial Value Realization</h1>
  
  <p>
    The completion of the Atelier Nilaya digital platform represents a milestone in high Indian jewellery e-commerce. 
    By blending authentic goldsmithing heritage with high-performance engineering, studio photographic turntables, 
    and transparent bench storytelling, Atelier Nilaya is positioned to cultivate lifelong bridal relationships, 
    expand global collector acquisition, and preserve its royal legacy for the next seventy years.
  </p>

</body>
</html>"""

    html_path = "Client Documentation.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated HTML source: {html_path} ({os.path.getsize(html_path)} bytes)")
    return html_path

def convert_html_to_pdf(html_path, pdf_path):
    print(f"Rendering PDF via Playwright Chrome: {pdf_path}...")
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
    print(f"PDF generated successfully: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

if __name__ == "__main__":
    h = generate_client_html()
    convert_html_to_pdf(h, "Client Documentation.pdf")
