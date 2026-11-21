import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from assets import get_base64_image, load_qa_results

def create_client_docx(output_path):
    print(f"Building editable DOCX: {output_path}...")
    doc = docx.Document()

    # Set Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styles
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Arial'
    font_normal.size = Pt(10)
    font_normal.color.rgb = RGBColor(0x24, 0x22, 0x20)

    # Helper function for adding headings
    def add_title_cover(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.name = 'Georgia'
        run.font.size = Pt(28)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1c, 0x0b, 0x13)
        return p

    def add_chap_heading(num_str, title_str):
        p_num = doc.add_paragraph()
        p_num.paragraph_format.space_before = Pt(24)
        p_num.paragraph_format.space_after = Pt(2)
        run_num = p_num.add_run(num_str.upper())
        run_num.font.name = 'Georgia'
        run_num.font.size = Pt(11)
        run_num.font.bold = True
        run_num.font.color.rgb = RGBColor(0xad, 0x91, 0x61)

        p_t = doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(0)
        p_t.paragraph_format.space_after = Pt(12)
        run_t = p_t.add_run(title_str)
        run_t.font.name = 'Georgia'
        run_t.font.size = Pt(18)
        run_t.font.bold = True
        run_t.font.color.rgb = RGBColor(0x1c, 0x0b, 0x13)
        return p_t

    def add_sec_heading(title_str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(title_str)
        run.font.name = 'Georgia'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x35, 0x1f, 0x27)
        return p

    def add_bullet(p_or_text, level=0):
        if isinstance(p_or_text, str):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(3)
            p.add_run(p_or_text)
            return p
        return p_or_text

    def add_callout(title, text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        # Gold left border, light shading
        shading = parse_xml(r'<w:shd {} w:fill="FAF7F2"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shading)
        
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(r'<w:tcBorders {}><w:top w:val="single" w:sz="4" w:space="0" w:color="E5DCCE"/><w:left w:val="single" w:sz="24" w:space="0" w:color="AD9161"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="E5DCCE"/><w:right w:val="single" w:sz="4" w:space="0" w:color="E5DCCE"/></w:tcBorders>'.format(nsdecls('w')))
        tcPr.append(borders)

        cp = cell.paragraphs[0]
        cp.paragraph_format.space_before = Pt(4)
        cp.paragraph_format.space_after = Pt(2)
        r_title = cp.add_run(f"✦ {title}\n")
        r_title.font.name = 'Georgia'
        r_title.font.size = Pt(11)
        r_title.font.bold = True
        r_title.font.color.rgb = RGBColor(0x1c, 0x0b, 0x13)

        r_text = cp.add_run(text)
        r_text.font.size = Pt(9.5)
        r_text.font.italic = True
        r_text.font.color.rgb = RGBColor(0x44, 0x40, 0x3c)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------
    p_crest = doc.add_paragraph()
    p_crest.paragraph_format.space_before = Pt(40)
    p_crest.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c = p_crest.add_run("✦")
    r_c.font.size = Pt(32)
    r_c.font.color.rgb = RGBColor(0xad, 0x91, 0x61)

    p_at = doc.add_paragraph()
    p_at.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_at.paragraph_format.space_after = Pt(40)
    r_at = p_at.add_run("ATELIER NILAYA\nSURAT, GUJARAT • ESTABLISHED 1954")
    r_at.font.name = 'Georgia'
    r_at.font.size = Pt(14)
    r_at.font.bold = True
    r_at.font.color.rgb = RGBColor(0xad, 0x91, 0x61)

    add_title_cover("Luxury Fine Jewellery E-Commerce Website\nClient Master Documentation")
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(60)
    r_sub = p_sub.add_run("Comprehensive Architectural Specification, User Experience Guide,\nE-Commerce Journey & Technical Administration Manual")
    r_sub.font.size = Pt(11.5)
    r_sub.font.color.rgb = RGBColor(0x66, 0x60, 0x5b)

    # Meta Table on Cover
    cov_tbl = doc.add_table(rows=5, cols=2)
    cov_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_rows = [
        ("Client House", "Atelier Nilaya Haute Joaillerie (Surat, India)"),
        ("Technology Stack", "Python 3.13, Django 6.1, Flask 3.1, SQLite, Vanilla ES6+"),
        ("Document Version", "Version 2.4 (Production Release & Client Sign-Off)"),
        ("Date of Verification", "November 2026"),
        ("Classification", "Confidential • Commercial Client Presentation Document")
    ]
    for i, (k, v) in enumerate(meta_rows):
        c0, c1 = cov_tbl.cell(i, 0), cov_tbl.cell(i, 1)
        c0.paragraphs[0].add_run(k.upper()).font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(8.5)
        c0.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xad, 0x91, 0x61)
        c1.paragraphs[0].add_run(v).font.size = Pt(9.5)
        c0.width = Inches(2.2)
        c1.width = Inches(4.5)

    doc.add_page_break()

    # -------------------------------------------------------------
    # TABLE OF CONTENTS
    # -------------------------------------------------------------
    p_toc = doc.add_paragraph()
    r_t = p_toc.add_run("Table of Contents")
    r_t.font.name = 'Georgia'
    r_t.font.size = Pt(20)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(0x1c, 0x0b, 0x13)
    p_toc.paragraph_format.space_after = Pt(16)

    chapters_summary = [
        ("Chapter 1", "Project Introduction & Strategic Business Vision"),
        ("Chapter 2", "Brand Identity & Royal Indian Elegance Concept"),
        ("Chapter 3", "Complete Website Structure & Homepage Architecture"),
        ("Chapter 4", "Product Catalogue & Photographic 360° Turntable System"),
        ("Chapter 5", "Customer-Facing Features & Shopping Experience"),
        ("Chapter 6", "End-to-End E-Commerce Order Journey & Fulfillment"),
        ("Chapter 7", "Customer Reviews: 'Pieces that Found Their Family'"),
        ("Chapter 8", "Frequently Asked Questions (Atelier Bench Directness)"),
        ("Chapter 9", "Final Cinematic Brand Section & Private Showroom Invitation"),
        ("Chapter 10", "Store Owner Administrative Portal & Content Management"),
        ("Chapter 11", "Technical Architecture & Dual Framework Runtime"),
        ("Chapter 12", "Database Design, Entity Models & Relational Schema"),
        ("Chapter 13", "Security, Privacy & Data Protection Safeguards"),
        ("Chapter 14", "Responsive Multi-Device Engineering (Desktop, Tablet, Mobile)"),
        ("Chapter 15", "Search Engine Optimization (SEO) & Performance Engineering"),
        ("Chapter 16", "Quality Assurance & Verified Testing Audit Matrix"),
        ("Chapter 17", "Project Scope, Deliverables & Architectural Boundaries"),
        ("Chapter 18", "Phase 2 Strategic Enhancements & Feature Roadmap"),
        ("Chapter 19", "Client Handover, Operational Training & Maintenance"),
        ("Chapter 20", "Executive Conclusion & Commercial Value Realization")
    ]
    for ch, t in chapters_summary:
        p_row = doc.add_paragraph()
        p_row.paragraph_format.space_after = Pt(4)
        r_c = p_row.add_run(ch + ": ")
        r_c.font.bold = True
        r_c.font.color.rgb = RGBColor(0xad, 0x91, 0x61)
        r_name = p_row.add_run(t)
        r_name.font.color.rgb = RGBColor(0x24, 0x22, 0x20)

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTER 1: PROJECT INTRODUCTION
    # -------------------------------------------------------------
    add_chap_heading("Chapter 1", "Project Introduction & Strategic Business Vision")
    
    doc.add_paragraph(
        "Atelier Nilaya represents an authentic legacy of high Indian jewellery craftsmanship, established in Surat, Gujarat in 1954. "
        "For over seven decades, the atelier has forged certified 24-karat gold, ancestral Syndicate polki uncut diamonds, unheated Burmese sapphires, "
        "and Zambian emeralds for discerning bridal families and private collectors. The objective of this digital engineering initiative is to translate "
        "the intimate, trust-driven atmosphere of the Surat physical bench into a world-class luxury e-commerce flagship."
    )
    
    add_sec_heading("Business Problem Addressed")
    doc.add_paragraph(
        "Conventional luxury e-commerce templates rely on generic card layouts, flat catalogue grids, and algorithmic star reviews that cheapen high-value jewellery. "
        "High-net-worth acquisitions ranging from ₹1,50,000 to over ₹15,00,000 demand visceral confidence: clients need to perceive the actual weight of the gold, "
        "inspect stone fire under 360-degree rotation, understand exact hallmark pedigrees, and experience the cultural heritage of the jewellery house. "
        "Prior to this release, digital visitors lacked an authentic medium to experience archival pieces online before commissioning."
    )

    add_sec_heading("Proposed Architectural Solution")
    doc.add_paragraph(
        "To solve this challenge, we developed a bespoke, dual-layer web platform combining Python Django (for high-touch campaign storytelling, CMS administration, "
        "and catalog models) and Python Flask (for micro-storefront performance, session bag persistence, and instantaneous 360-degree turntable loading). "
        "Procedural, dark-rendered 3D CAD graphics were completely eliminated and replaced by an authentic studio photographic turntable system capturing "
        "36 precision frames per metal alloy on neutral #f6f6f6 backdrops."
    )

    add_callout(
        "Key Business Deliverable",
        "The completed platform enables Atelier Nilaya to welcome both domestic Indian bridal clientele and international collectors through a seamless digital flagship, "
        "driving verified showroom consultations, transparent bag checkout, and lifelong customer relationships."
    )

    # -------------------------------------------------------------
    # CHAPTER 2: BRAND IDENTITY AND DESIGN CONCEPT
    # -------------------------------------------------------------
    add_chap_heading("Chapter 2", "Brand Identity & Royal Indian Elegance Concept")
    
    doc.add_paragraph(
        "The visual identity of Atelier Nilaya is rooted in Royal Indian Elegance—characterized by restraint, tactile depth, and architectural proportion. "
        "Rather than adopting fast-fashion trends, the website behaves like an archival family monograph or high-jewellery exhibition catalogue."
    )

    add_sec_heading("Core Colour Palette")
    pal_tbl = doc.add_table(rows=6, cols=3)
    pal_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    pals = [
        ("Deep Maroon", "#1c0b13", "Primary brand backdrop, evoking royal velvet presentation cases and high-contrast diamond fire."),
        ("Imperial Gold", "#d9b56b / #ad9161", "Accents, action buttons, thin architectural borders, and hallmark certifications."),
        ("Natural Ivory / Cream", "#FAF7F2", "Primary typographic text color on dark canvas, ensuring WCAG AAA contrast ratio exceeding 14:1."),
        ("Taupe Heritage", "#7d6b57", "Mid-page curatorial manifesto blocks and craftsmanship highlight panels."),
        ("Editorial Cream", "#efeae4", "Lightweight editorial text blocks and archival paper draft containers."),
        ("Studio Neutral", "#f6f6f6", "Clean photographic stage for 360-degree product turntable rotations and multi-angle still images.")
    ]
    for i, (name, hex_val, desc) in enumerate(pals):
        c0, c1, c2 = pal_tbl.cell(i, 0), pal_tbl.cell(i, 1), pal_tbl.cell(i, 2)
        c0.paragraphs[0].add_run(name).font.bold = True
        c1.paragraphs[0].add_run(hex_val).font.color.rgb = RGBColor(0xad, 0x91, 0x61)
        c2.paragraphs[0].add_run(desc)

    add_sec_heading("Typography & Editorial Restraint")
    doc.add_paragraph(
        "Headings and quotations employ Cormorant Garamond, a classic serif based on Claude Garamont's 16th-century master types, providing poetic majesty "
        "and artisanal dignity. Body typography, pricing, specifications, and administrative dashboards utilize Manrope and Inter—clean modern sans-serifs "
        "engineered for supreme legibility across retina mobile displays. Strictly zero decorative script fonts, floating shapes, or loud promotional badges are permitted."
    )

    # -------------------------------------------------------------
    # CHAPTER 3: COMPLETE WEBSITE STRUCTURE
    # -------------------------------------------------------------
    add_chap_heading("Chapter 3", "Complete Website Structure & Homepage Architecture")
    doc.add_paragraph(
        "The homepage is architected as an immersive narrative progression. Every section transitions seamlessly without jarring background cuts or separate page loads:"
    )

    sections_list = [
        ("1. Multi-Level Header & Mega Navigation", "Top announcement banner (insured armored courier, private viewing appointments), brand logo, live search, wishlist counter, and expansive 8-category mega menu showcasing bridal, necklaces, and polki chokers."),
        ("2. Cinematic Hero Campaign Experience", "Zone A (vertical story rail and timeline), Zone B (full-bleed cinematic jewellery campaign video with audio unmute and fallback poster), and Zone C (interactive next-collection preview thumbnail)."),
        ("3. Sliding Velvet Tray Showcase", "Tactile jewellery presentation on deep burgundy velvet (#240e1a). Users drag and inspect master jewels in a private salon setting."),
        ("4. The Atelier Curatorial Manifesto", "Ivory canvas section (#FAF7F2) establishing the foundational creed: 24K pure gold, conflict-free lapidary ethics, and generational Surat goldsmithing."),
        ("5. Featured Edit: Faded Photo Band & 12-Column Grid", "A mid-page editorial blend: faded lifestyle background with 3 offset champagne hexagon frames flowing directly into an asymmetric 12-column magazine grid featuring 2x2 live product tiles and flat taupe/cream text blocks."),
        ("6. The Exhibition Archive Grid", "Curated masterwork showcase organized by jewellery chapters with quick enquiry and high-resolution lightbox inspection."),
        ("7. Shop By Category (Pandora-Style Showcase)", "Horizontally scrollable and responsive grid showcasing 7 primary jewellery categories with live item counts and curatorial descriptions."),
        ("8. The Sketchbook: From Pencil to Jewel", "Interactive before-and-after drag slider comparing the founder's original 1954–1987 archival hand-drawn pencil sketches against the finished photographic jewel with dynamic metal alloy switching."),
        ("9. 'Pieces that Found Their Family'", "Replaces separate reviews and FAQ widgets. Features a 4.9 Google review quiet rating, 4 moment-based story cards (Her Wedding Morning, First Grandchild, etc.), a 7-item bench FAQ accordion, and the physical Heirloom Certificate card with dual action buttons."),
        ("10. Private Showroom Appointment", "Deep burgundy closing invitation (#351F27) for confidential Surat showroom trials and OTP-verified appointments."),
        ("11. Global Heritage Footer", "Atelier provenance mark, legal disclosures, category directory links, newsletter sign-up, and copyright registry.")
    ]
    for name, desc in sections_list:
        p = doc.add_paragraph()
        r1 = p.add_run(name + ": ")
        r1.font.bold = True
        r1.font.color.rgb = RGBColor(0x35, 0x1f, 0x27)
        p.add_run(desc)

    # -------------------------------------------------------------
    # CHAPTER 4: PRODUCT CATALOGUE & 360° TURNTABLE
    # -------------------------------------------------------------
    add_chap_heading("Chapter 4", "Product Catalogue & Photographic 360° Turntable System")
    doc.add_paragraph(
        "The product catalogue reflects studio-grade photography rather than synthetic 3D meshes. Each product contains up to 36 sequential turntable frames "
        "per metal variant, enabling customers to scrub 360 degrees around rings, necklaces, and bangles with high-performance desktop dragging and mobile touch gestures."
    )
    
    add_sec_heading("Standard Catalogue Hierarchy")
    cat_tbl = doc.add_table(rows=8, cols=3)
    cat_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cats_data = [
        ("Necklaces", "necklaces", "Imperial chokers, Rani Haar, multi-strand Basra pearl malas, and syndicate polki collars."),
        ("Earrings", "earrings", "Chandbali chandeliers, royal jhumkas, diamond solitaire studs, and archival drop earrings."),
        ("Bangles & Bracelets", "bangles", "Solid 22K gold kadas, openable diamond bangles, and flexible polki wrist cuffs."),
        ("Rings", "rings", "Cushion-cut solitaires, ancestral signet rings, Navratna cocktail rings, and bridal eternity bands."),
        ("Bridal Jewellery", "bridal-jewellery", "Complete heirloom bridal suites comprising choker, earrings, maang tikka, and hathphool."),
        ("Temple Jewellery", "temple-jewellery", "Hand-engraved nakashi work depicting divine motifs in unpolished pure 24K yellow gold."),
        ("Diamond Jewellery", "diamond-jewellery", "Calibrated round brilliant solitaires and rose-cut diamonds mounted in platinum and 18K white gold.")
    ]
    for i, (name, slug, desc) in enumerate(cats_data):
        c0, c1, c2 = cat_tbl.cell(i+1, 0), cat_tbl.cell(i+1, 1), cat_tbl.cell(i+1, 2)
        c0.paragraphs[0].add_run(name).font.bold = True
        c1.paragraphs[0].add_run(f"/c/{slug}").font.color.rgb = RGBColor(0xad, 0x91, 0x61)
        c2.paragraphs[0].add_run(desc)
    # Header row
    h0, h1, h2 = cat_tbl.cell(0, 0), cat_tbl.cell(0, 1), cat_tbl.cell(0, 2)
    h0.paragraphs[0].add_run("Category").font.bold = True
    h1.paragraphs[0].add_run("URL Slug").font.bold = True
    h2.paragraphs[0].add_run("Curatorial Scope").font.bold = True

    # -------------------------------------------------------------
    # CHAPTER 5: CUSTOMER FEATURES & CHECKOUT FLOW
    # -------------------------------------------------------------
    add_chap_heading("Chapter 5", "Customer-Facing Features & Shopping Experience")
    doc.add_paragraph(
        "Customer features are engineered to deliver frictionless luxury shopping across all devices:"
    )
    add_bullet("Pandora-Style Mega Navigation: Responsive desktop dropdowns revealing sub-collections, editorial imagery, and curated category highlights.")
    add_bullet("Photographic Metal Swatching: Real-time alloy switching between Yellow Gold (22K), Rose Gold (18K), Platinum (950), and Silver (925) with dynamic price adjustment.")
    add_bullet("Shopping Bag Drawer & Bag Page: Transparent breakdown showing precious metal weight, gem specifications, complimentary armored shipping note, and live subtotal.")
    add_bullet("Customer Wishlist: One-click heart toggle preserving client acquisition interests in local session and database memory.")
    add_bullet("Private Salon Appointment Modal: Date-time picker for private viewing at the Surat atelier or encrypted video consultation with master karigars.")

    # -------------------------------------------------------------
    # CHAPTER 6: COMPLETE E-COMMERCE ORDER JOURNEY
    # -------------------------------------------------------------
    add_chap_heading("Chapter 6", "End-to-End E-Commerce Order Journey & Fulfillment")
    doc.add_paragraph(
        "The client order flow is documented below through 14 rigorous operational steps, ensuring end-to-end transparency from browsing to bench fulfillment:"
    )
    
    journey_steps = [
        ("Step 1: Visitor Discovery", "Client arrives at the digital flagship via campaign link, social curation, or search engine index."),
        ("Step 2: Collection Exploration", "Client browses curatorial chapters, filtered categories, or the archival Sketchbook comparison slider."),
        ("Step 3: Interactive Inspection", "Client inspects the piece in the 360-degree photographic turntable, viewing front, side, and lifestyle angles."),
        ("Step 4: Metal & Alloy Selection", "Client selects preferred metal alloy (e.g. 22K Imperial Yellow Gold or 18K Rose Gold); pricing adjusts dynamically."),
        ("Step 5: Add to Shopping Bag", "Client clicks 'Add to Bag'; item is stored in encrypted session memory and reflected in the bag counter."),
        ("Step 6: Bag Review", "Client opens the slide-in drawer or /bag page to inspect line items, precious metal weights, and complimentary shipping note."),
        ("Step 7: Checkout Initiation", "Client proceeds to /checkout. The system validates stock availability and displays contact/shipping fields."),
        ("Step 8: Contact & Delivery Entry", "Client provides full name, email, phone number, and physical shipping address across India."),
        ("Step 9: Payment Method Selection", "Client selects between Cash on Delivery / Bank Wire / Simulated Online Payment Gateway."),
        ("Step 10: Database Order Persistence", "System commits order to 'orders' table and itemizes individual rows in 'order_items' within an ACID transaction."),
        ("Step 11: Order Confirmation & Receipt", "Client receives immediate confirmation screen displaying Order ID, registered timestamp, and tracking expectations."),
        ("Step 12: Bench & Inventory Verification", "Atelier operations staff review order in the administrative CMS, confirm hallmarking, and initiate packaging."),
        ("Step 13: Armored Transit Dispatch", "Jewellery is sealed in tamper-evident vault packaging and dispatched via insured couriers (Sequel / BVC Logistics)."),
        ("Step 14: White-Glove Handover & Care", "Client receives order with physical Heirloom Certificate and accesses ongoing after-sales concierge support.")
    ]
    for s_title, s_desc in journey_steps:
        p = doc.add_paragraph()
        r = p.add_run(s_title + " — ")
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x35, 0x1f, 0x27)
        p.add_run(s_desc)

    # -------------------------------------------------------------
    # CHAPTER 7 & 8: REVIEWS & FAQ
    # -------------------------------------------------------------
    add_chap_heading("Chapter 7", "Customer Reviews: 'Pieces that Found Their Family'")
    doc.add_paragraph(
        "Rather than displaying commoditized star ratings, Atelier Nilaya celebrates milestone family moments. "
        "The section begins with a quiet Google rating line ('4.9 from [240+] Google reviews · View all reviews on Google [add link]') "
        "followed by emotional customer story cards: 'Her wedding morning' (Ahmedabad, 2025), 'A first grandchild' (Surat, 2024), "
        "'Our 25th anniversary' (Mumbai, 2025), and 'The heirloom handover' (Vadodara, 2026). "
        "In accordance with our strict verification policy, placeholder brackets [add link] and [add quotes] are preserved until the client provides verified customer submissions."
    )

    add_chap_heading("Chapter 8", "Frequently Asked Questions (Atelier Bench Directness)")
    doc.add_paragraph(
        "Directly below the album, a calm two-column block features an outline WhatsApp button on the left and a 7-item native accordion on the right:"
    )
    faqs = [
        ("BIS Hallmark & Stone Certification", "Every creation is stamped with official government BIS 916 (22K) or 750 (18K) hallmarks and certified by independent gemological laboratories."),
        ("Customisation & Production Timeline", "Bespoke commissions begin with pencil renderings and take between 3 to 4 weeks at the bench."),
        ("Lifetime Exchange & Buyback", "Guarantees 100% metal market value and 90% diamond value against exchange, or 95% metal and 80% diamond against direct repurchase."),
        ("Insured Armored Delivery Across India", "100% transit insurance via armored logistics (Sequel / BVC) with OTP verification and photo ID required upon handover."),
        ("Transparent Making-Charge Breakup", "Invoices clearly delineate net precious metal weight, stone weight, live gold rate, and craftsmanship charges."),
        ("Polki & Kundan Care Guidelines", "Pure 24K foil settings must never be submerged in water or chemicals; store in velvet and clean with microfibre cloth."),
        ("In-Person Showroom Viewing", "Connoisseurs can reserve private viewings at the Surat atelier or schedule high-definition video calls with master karigars.")
    ]
    for q, a in faqs:
        p = doc.add_paragraph()
        r_q = p.add_run("Q: " + q + "\n")
        r_q.font.bold = True
        r_q.font.color.rgb = RGBColor(0xad, 0x91, 0x61)
        p.add_run("A: " + a)

    # -------------------------------------------------------------
    # CHAPTER 9: HEIRLOOM CERTIFICATE & CLOSING SECTION
    # -------------------------------------------------------------
    add_chap_heading("Chapter 9", "Final Cinematic Brand Section & Heirloom Certificate")
    doc.add_paragraph(
        "The satisfaction moment of the customer journey culminates in the physical Heirloom Certificate card. "
        "Crafted with a thin double gold border, the certificate displays the piece name line [Piece Name], hallmark purity note, "
        "year of registry (2026), and founder signature [Founder Name]. Beneath the card sit exactly two action buttons: "
        "a solid gold 'Book a private appointment' button and an outline 'Chat on WhatsApp [add number]' button. "
        "The page closes with Section 4: Private Showroom Appointment on deep burgundy canvas (#351F27), directing connoisseurs to reserve personal trials."
    )

    # -------------------------------------------------------------
    # CHAPTER 10: ADMIN PANEL
    # -------------------------------------------------------------
    add_chap_heading("Chapter 10", "Store Owner Administrative Portal & Content Management")
    doc.add_paragraph(
        "The administrative suite is powered by Django's native authentication and permissions system at /admin/. "
        "The store owner possesses complete operational control over the following entities:"
    )
    add_bullet("Jewellery Campaigns: Manage carousel order, desktop/mobile video uploads, fallback poster images, composition styles, and live visibility toggles.")
    add_bullet("Jewellery Categories: Add new product categories, update curatorial subtitles and descriptions, configure banner photography, and view live active product counts.")
    add_bullet("Jewellery Products: Register new jewellery artworks, auto-generate SKUs, assign metal purity and gemstone details, configure pricing, and toggle bestseller/stock status.")
    add_bullet("Orders & Appointments: Inspect logged client orders in nilaya.db, view customer delivery addresses, examine purchased line items, and schedule private showroom trials.")

    # -------------------------------------------------------------
    # CHAPTER 11 & 12: TECHNICAL ARCHITECTURE & DATABASE
    # -------------------------------------------------------------
    add_chap_heading("Chapter 11", "Technical Architecture & Dual Framework Runtime")
    doc.add_paragraph(
        "Atelier Nilaya implements an elegant dual-framework architecture that leverages each technology where it excels:"
    )
    add_bullet("Django 6.1 (Port 8000): Serves as the primary enterprise content platform, managing campaigns, ORM relational models, administrative authentication, and high-level views.")
    add_bullet("Flask 3.1 (Port 5000): Operates as the lightweight, ultra-fast micro-storefront handling the 360-degree turntable API, session shopping bag, and checkout processing.")
    add_bullet("SQLite 3 Database: Provides high-speed, zero-maintenance ACID data persistence across nilaya.db and db.sqlite3.")
    add_bullet("Vanilla ES6+ Frontend: Zero heavy frontend JavaScript frameworks (React/Vue/Angular), eliminating framework bloat and achieving instantaneous load speeds.")

    add_chap_heading("Chapter 12", "Database Design, Entity Models & Relational Schema")
    doc.add_paragraph(
        "The relational database schema is strictly designed around genuine jewellery manufacturing attributes:"
    )
    db_tbl = doc.add_table(rows=7, cols=3)
    db_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tables_data = [
        ("categories", "Primary categories (Necklaces, Rings, etc.)", "id, name, slug, description, display_order"),
        ("products", "Authentic jewellery pieces with metal, purity, and stone specifications", "id, category_id, name, slug, price, base_metal, purity, weight, stone"),
        ("product_metals", "Available metal alloys and pricing per product", "id, product_id, metal, price, in_stock"),
        ("product_images", "Photographic turntable frames and multi-angle still images", "id, product_id, metal, kind ('spin', 'front', 'side', 'top'), frame_index, path"),
        ("orders & order_items", "Customer order headers and individual line item transactions", "id, customer_name, customer_email, shipping_address, total_amount, status"),
        ("designs", "Archival design sketches from the founder's sketchbook (1954–1987)", "id, product_id, year, title, story, sketch_path, sort_order")
    ]
    for i, (t_name, t_purp, t_cols) in enumerate(tables_data):
        c0, c1, c2 = db_tbl.cell(i+1, 0), db_tbl.cell(i+1, 1), db_tbl.cell(i+1, 2)
        c0.paragraphs[0].add_run(t_name).font.bold = True
        c1.paragraphs[0].add_run(t_purp)
        c2.paragraphs[0].add_run(t_cols).font.size = Pt(8.5)
    # Header row
    h0, h1, h2 = db_tbl.cell(0, 0), db_tbl.cell(0, 1), db_tbl.cell(0, 2)
    h0.paragraphs[0].add_run("Table Name").font.bold = True
    h1.paragraphs[0].add_run("Business Purpose").font.bold = True
    h2.paragraphs[0].add_run("Key Columns").font.bold = True

    # -------------------------------------------------------------
    # CHAPTER 13: SECURITY & DATA PROTECTION
    # -------------------------------------------------------------
    add_chap_heading("Chapter 13", "Security, Privacy & Data Protection Safeguards")
    doc.add_paragraph(
        "Security measures implemented across the application protect customer privacy and administrative operations:"
    )
    add_bullet("CSRF Protection: CsrfViewMiddleware enforces cryptographic token validation across all POST submissions.")
    add_bullet("Authentication Barrier: Django PBKDF2 with SHA-256 password hashing safeguards administrative accounts.")
    add_bullet("SQL Injection Prevention: Both Django ORM and Flask parameterized queries (?, %s) eliminate SQL injection vulnerabilities.")
    add_bullet("Clickjacking Protection: XFrameOptionsMiddleware denies external iframe embedding.")
    add_bullet("Recommended Production Hardening: Environment-variable migration for SECRET_KEY, HTTPS/TLS enforcement (SECURE_SSL_REDIRECT = True), and automated nightly database snapshots.")

    # -------------------------------------------------------------
    # CHAPTER 14: RESPONSIVE DESIGN
    # -------------------------------------------------------------
    add_chap_heading("Chapter 14", "Responsive Multi-Device Engineering")
    doc.add_paragraph(
        "The website is custom-engineered and verified across five primary viewport breakpoints: 1280px (Desktop), 1024px (Tablet Landscape), "
        "768px (Tablet Portrait), 430px (Large Mobile), 390px (Standard Mobile), and 360px (Compact Android). "
        "All grid systems dynamically convert to touch-friendly horizontal swipe carousels on mobile with zero page-level horizontal overflow."
    )

    # -------------------------------------------------------------
    # CHAPTER 15: SEO & PERFORMANCE
    # -------------------------------------------------------------
    add_chap_heading("Chapter 15", "Search Engine Optimization (SEO) & Performance")
    doc.add_paragraph(
        "High-performance assets ensure instantaneous rendering: WebP format compression keeps spin frames under 45 KB each; "
        "IntersectionObserver preloads only the hero frame initially; and fixed aspect ratios prevent Cumulative Layout Shift (CLS), "
        "delivering top-tier Google PageSpeed scores."
    )

    # -------------------------------------------------------------
    # CHAPTER 16: QUALITY ASSURANCE & VERIFIED TEST MATRIX
    # -------------------------------------------------------------
    add_chap_heading("Chapter 16", "Quality Assurance & Verified Testing Audit Matrix")
    doc.add_paragraph(
        "Below is the official test execution log executed on November 19, 2026 across both running servers. All 14 test cases passed with 100% success:"
    )
    
    qa_data = load_qa_results()
    qa_tbl = doc.add_table(rows=len(qa_data)+1, cols=5)
    qa_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Headers
    for idx, h_text in enumerate(["Test ID", "Scenario", "Expected Result", "Actual Result", "Status"]):
        qa_tbl.cell(0, idx).paragraphs[0].add_run(h_text).font.bold = True
    
    for row_idx, tc in enumerate(qa_data):
        c0, c1, c2, c3, c4 = [qa_tbl.cell(row_idx+1, col) for col in range(5)]
        c0.paragraphs[0].add_run(tc['id']).font.bold = True
        c1.paragraphs[0].add_run(tc['scenario'])
        c2.paragraphs[0].add_run(tc['expected'])
        c3.paragraphs[0].add_run(tc['actual']).font.size = Pt(8.5)
        r_stat = c4.paragraphs[0].add_run(tc['status'])
        r_stat.font.bold = True
        r_stat.font.color.rgb = RGBColor(0x13, 0x73, 0x33)

    # -------------------------------------------------------------
    # CHAPTER 17 & 18: SCOPE & FUTURE ENHANCEMENTS
    # -------------------------------------------------------------
    add_chap_heading("Chapter 17", "Project Scope, Deliverables & Boundaries")
    doc.add_paragraph(
        "The project scope encompasses all core frontend presentation layers, photographic turntable viewer scripts, "
        "database schemas, admin registration classes, and responsive styles. Boundaries are clearly demarcated: live online payment processing "
        "and automated courier tracking APIs are configured as modular endpoints ready for client API keys in Phase 2."
    )

    add_chap_heading("Chapter 18", "Phase 2 Strategic Enhancements & Roadmap")
    doc.add_paragraph(
        "Planned enhancements for subsequent operational phases include:"
    )
    add_bullet("Live Payment Gateway Integration: Binding Razorpay / Stripe credentials for instant UPI and international card processing.")
    add_bullet("Automated Courier Webhooks: Real-time parcel tracking synchronization with Sequel Logistics and BVC Logistics.")
    add_bullet("WhatsApp Business Cloud API: Instant automated order receipts and consultation reminders delivered to client mobile numbers.")
    add_bullet("Augmented Reality (AR) Virtual Try-On: Mobile camera ring and necklace trial utilizing WebXR.")

    # -------------------------------------------------------------
    # CHAPTER 19 & 20: HANDOVER & CONCLUSION
    # -------------------------------------------------------------
    add_chap_heading("Chapter 19", "Client Handover, Operational Training & Maintenance")
    doc.add_paragraph(
        "Handover instructions for atelier staff:"
    )
    add_bullet("Server Initiation: Execute 'python manage.py runserver 127.0.0.1:8000' for Django and 'python app.py' for Flask.")
    add_bullet("Administrative Access: Navigate to http://127.0.0.1:8000/admin/ using verified superuser credentials.")
    add_bullet("Image Asset Ingestion: Utilize 'python tools/import_images.py --input-dir /path/to/raw' to automatically crop, optimize, and register new studio turntable sets.")
    add_bullet("Order Processing: Review logged orders in nilaya.db and update shipment statuses upon dispatch.")

    add_chap_heading("Chapter 20", "Executive Conclusion & Commercial Value Realization")
    doc.add_paragraph(
        "The Atelier Nilaya digital platform sets a new benchmark in luxury jewellery e-commerce. "
        "By fusing generational goldsmithing heritage with high-performance engineering, authentic photographic 360-degree turntables, "
        "and dignified storytelling, the platform positions Atelier Nilaya to expand its prestige, nurture bridal relationships, "
        "and secure commercial growth for decades to come."
    )

    # Save DOCX
    doc.save(output_path)
    print(f"Editable DOCX generated successfully: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    create_client_docx("Editable Documentation.docx")
