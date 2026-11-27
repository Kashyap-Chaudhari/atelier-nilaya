import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unveiling_atelier.settings')

import django
django.setup()

import re
from django.test import Client
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from campaigns.models import JewelleryProduct, JewelleryCategory, GoldRate
from orders.models import Order


def audit_website():
    client = Client()
    issues = []
    
    print("==================================================")
    print("COMPREHENSIVE CUSTOMER-FACING AUDIT")
    print("==================================================")

    # 1. Audit Home Page
    resp = client.get('/')
    assert resp.status_code == 200
    home_html = resp.content.decode()

    # Check for dead '#' links on Home Page
    hash_links = re.findall(r'href=[\'"](#[\w\-]*)[\'"]', home_html)
    for h in set(hash_links):
        if h == '#' or (len(h) > 1 and f'id="{h[1:]}"' not in home_html and f"id='{h[1:]}'" not in home_html):
            issues.append({
                'id': f'ISSUE-HOME-DEADLINK-{h}',
                'component': 'Home Page / Links',
                'severity': 'Medium',
                'desc': f'Dead or unanchored link href="{h}" found on Home page.',
                'fix': f'Point {h} to actual section ID or live URL.'
            })

    # Check footer policy links
    for policy in ['/privacy-policy/', '/terms/', '/shipping-returns/', '/care-guide/', '/size-guide/']:
        p_resp = client.get(policy)
        if p_resp.status_code == 404:
            issues.append({
                'id': f'ISSUE-POLICY-{policy.strip("/")}',
                'component': 'Service & Policy Pages',
                'severity': 'High',
                'desc': f'Policy page {policy} returns 404 Not Found when clicked from footer or signup consent.',
                'fix': f'Implement dedicated policy & care guide view/template for {policy}.'
            })

    # 2. Audit All Categories & Slugs
    categories = JewelleryCategory.objects.all()
    for cat in categories:
        cat_url = f'/c/{cat.slug}/'
        c_resp = client.get(cat_url)
        if c_resp.status_code != 200:
            issues.append({
                'id': f'ISSUE-CAT-{cat.slug}',
                'component': f'Collection Page ({cat.name})',
                'severity': 'Critical',
                'desc': f'Collection page {cat_url} failed with HTTP {c_resp.status_code}.',
                'fix': 'Ensure category products view handles category cleanly.'
            })
        else:
            cat_html = c_resp.content.decode()
            # Check pagination / "Showing X of Y"
            if 'Showing' not in cat_html and 'pieces' not in cat_html:
                issues.append({
                    'id': f'ISSUE-CAT-COUNT-{cat.slug}',
                    'component': f'Collection Page ({cat.name})',
                    'severity': 'Medium',
                    'desc': f'Category {cat.name} lacks clear "Showing X of Y pieces" indicator.',
                    'fix': 'Add item count and range counter.'
                })

    # 3. Audit All Active Products (Images, 360 Spin, Pricing)
    products = JewelleryProduct.objects.all()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for prod in products:
        p_url = f'/p/{prod.slug}/'
        p_resp = client.get(p_url)
        if p_resp.status_code != 200:
            issues.append({
                'id': f'ISSUE-PROD-{prod.id}',
                'component': f'Product Page ({prod.name})',
                'severity': 'Critical',
                'desc': f'Product page {p_url} returned HTTP {p_resp.status_code}.',
                'fix': 'Fix product detail resolution.'
            })
            continue

        p_html = p_resp.content.decode()

        # Check 360 spin viewer: only show when frames really exist
        spin_dir = os.path.join(base_dir, 'static', 'products', prod.slug, 'platinum', 'spin')
        spin_frames_exist = os.path.exists(spin_dir) and len(os.listdir(spin_dir)) >= 10
        if not spin_frames_exist:
            # Check yellow_gold
            spin_dir_yg = os.path.join(base_dir, 'static', 'products', prod.slug, 'yellow_gold', 'spin')
            spin_frames_exist = os.path.exists(spin_dir_yg) and len(os.listdir(spin_dir_yg)) >= 10

        has_spin_markup = 'data-spin' in p_html or 'spin-viewer' in p_html or '360' in p_html
        if not spin_frames_exist and has_spin_markup:
            # Check if 360 button is displayed to customer despite missing frames
            if 'aaranya-360-btn' in p_html and not spin_frames_exist:
                issues.append({
                    'id': f'ISSUE-SPIN-{prod.slug}',
                    'component': f'Product 360 Viewer ({prod.name})',
                    'severity': 'High',
                    'desc': f'Product {prod.name} displays 360 interactive button but real spin frames are absent.',
                    'fix': 'Only render 360 viewer trigger when real spin frames exist in catalog.'
                })

        # Check delivery pincode checker on product page
        if 'pincode' not in p_html.lower() and 'estimate' not in p_html.lower():
            issues.append({
                'id': f'ISSUE-PINCODE-{prod.slug}',
                'component': f'Product Delivery Estimator ({prod.name})',
                'severity': 'High',
                'desc': f'Product {prod.name} lacks inline pincode check / delivery estimator.',
                'fix': 'Embed real pincode verification and delivery window widget on product page.'
            })

    # 4. Audit Order Lifecycle & Post-Purchase (Cancellation, Returns, Exchanges)
    orders = Order.objects.all()
    for o in orders[:3]:
        t_resp = client.get(f'/orders/track/{o.order_number}/')
        if t_resp.status_code != 200:
            issues.append({
                'id': f'ISSUE-TRACK-{o.order_number}',
                'component': 'Order Tracking Page',
                'severity': 'High',
                'desc': f'Tracking page for {o.order_number} returned {t_resp.status_code}',
                'fix': 'Fix tracking timeline view.'
            })

        inv_resp = client.get(f'/orders/invoice/{o.order_number}/')
        if inv_resp.status_code != 200:
            issues.append({
                'id': f'ISSUE-INV-{o.order_number}',
                'component': 'Order Invoice View',
                'severity': 'High',
                'desc': f'Invoice for {o.order_number} returned {inv_resp.status_code}',
                'fix': 'Ensure invoice renders cleanly.'
            })

    # 5. Check 404 and 500 error templates
    not_found_resp = client.get('/nonexistent-test-url-1954/')
    if not_found_resp.status_code == 404:
        nf_html = not_found_resp.content.decode()
        if 'Atelier' not in nf_html and 'Nilaya' not in nf_html:
            issues.append({
                'id': 'ISSUE-404-STYLING',
                'component': 'Error Pages (404)',
                'severity': 'High',
                'desc': '404 page renders standard debug or default unbranded server page instead of luxury Atelier Nilaya 404 page.',
                'fix': 'Provide custom branded 404.html template with return to boutique button.'
            })

    print(f"\nAudit complete. Found {len(issues)} customer-facing issues.")
    for iss in issues:
        print(f"[{iss['severity']}] {iss['id']} ({iss['component']}): {iss['desc']}")

    return issues


if __name__ == '__main__':
    audit_website()
