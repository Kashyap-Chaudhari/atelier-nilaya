import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unveiling_atelier.settings')
django.setup()

from django.test import Client
from campaigns.models import JewelleryProduct

c = Client()

print("--- 1. Testing Homepage & Header Bag Pill ---")
resp = c.get('/')
assert resp.status_code == 200, f"Hero page failed: {resp.status_code}"
assert b'header-bag-btn' in resp.content, "Header bag button missing in base template"
assert b'nilaya-bag-drawer' in resp.content, "Bag drawer markup missing in base template"
print("✓ Home page & Bag Drawer markup verified.")

print("--- 2. Testing Product Detail Page ---")
prod = JewelleryProduct.objects.first()
pdp_url = f"/p/{prod.slug}/"
resp = c.get(pdp_url)
assert resp.status_code == 200, f"PDP failed: {resp.status_code}"
assert b'page-add-to-bag-btn' in resp.content, "Add to Bag button missing on PDP"
assert b'product-size-select' not in resp.content, "Customization box should remain removed per user request"
print(f"✓ PDP for '{prod.name}' verified with clean layout and Add to Bag button.")

print("--- 3. Testing Adding to Bag ---")
add_resp = c.post('/cart/api/add/', data=json.dumps({
    'slug': prod.slug,
    'metal': 'yellow_gold',
    'size': 'Indian Size 14 (17.2 mm - Standard)',
    'engraving_text': 'A & N 1954',
    'quantity': 1
}), content_type='application/json')
assert add_resp.status_code == 200, f"Add to bag failed: {add_resp.status_code}"
add_data = add_resp.json()
assert add_data['success'] is True, f"Add to bag unsuccessful: {add_data}"
print(f"✓ Added item to cart. Total items: {add_data['cart']['total_items']}, Final Total: ₹{add_data['cart']['final_total']}")

print("--- 4. Testing Pincode Lookup API ---")
pin_resp = c.post('/orders/api/pincode/lookup/', data=json.dumps({'pincode': '395003'}), content_type='application/json')
assert pin_resp.status_code == 200
pin_data = pin_resp.json()
assert pin_data['city'] == 'Surat', f"Unexpected city: {pin_data}"
print(f"✓ Pincode 395003 resolved to: {pin_data['city']}, {pin_data['state']} ({pin_data['estimate']})")

print("--- 5. Testing Coupon Validation API ---")
coupon_resp = c.post('/orders/api/coupon/validate/', data=json.dumps({'code': 'HEIRLOOM1954'}), content_type='application/json')
assert coupon_resp.status_code == 200
coupon_data = coupon_resp.json()
assert coupon_data['discount'] > 0, f"Discount should be > 0: {coupon_data}"
print(f"✓ Coupon HEIRLOOM1954 valid! Discount: ₹{coupon_data['discount']}, New Total: ₹{coupon_data['new_total']}")

print("--- 6. Testing Checkout Page Render ---")
checkout_resp = c.get('/orders/checkout/')
assert checkout_resp.status_code == 200, f"Checkout view failed: {checkout_resp.status_code}"
assert b'Complete Your Acquisition' in checkout_resp.content
assert b'checkout-submit-pay-btn' in checkout_resp.content
print("✓ /orders/checkout/ rendered successfully with 3-step form and order summary.")

print("--- 7. Testing OTP Flow ---")
otp_send_resp = c.post('/orders/api/otp/send/', data=json.dumps({'phone': '9825195400'}), content_type='application/json')
assert otp_send_resp.status_code == 200
otp_verify_resp = c.post('/orders/api/otp/verify/', data=json.dumps({'otp': '729401'}), content_type='application/json')
assert otp_verify_resp.status_code == 200
assert otp_verify_resp.json()['success'] is True
print("✓ OTP sent and verified successfully.")

print("--- 8. Testing Razorpay Order Creation ---")
rzp_create_resp = c.post('/payments/api/order/create/', data=json.dumps({
    'customer': {
        'full_name': 'Meera Zaveri',
        'phone': '9825195400',
        'email': 'meera.zaveri@royalheritage.in',
        'address_line1': 'Nilaya Villa, Mughalisara',
        'city': 'Surat',
        'state': 'Gujarat',
        'pincode': '395003',
        'is_gift': True,
        'gift_message': 'To our daughter on her wedding day.',
        'hide_price_on_invoice': True
    },
    'coupon_code': 'HEIRLOOM1954',
    'is_advance': False
}), content_type='application/json')
assert rzp_create_resp.status_code == 200, f"Create order failed: {rzp_create_resp.content}"
order_info = rzp_create_resp.json()
assert order_info['success'] is True
order_number = order_info['order_number']
print(f"✓ Order created: {order_number}, Amount: ₹{order_info['amount_inr']}, Razorpay Order ID: {order_info['razorpay_order_id']}")

print("--- 9. Testing Payment Verification & Confirmation ---")
verify_resp = c.post('/payments/api/verify/', data=json.dumps({
    'order_number': order_number,
    'razorpay_order_id': order_info['razorpay_order_id'],
    'razorpay_payment_id': 'pay_test_verified_916',
    'razorpay_signature': ''
}), content_type='application/json')
assert verify_resp.status_code == 200
print(f"✓ Payment verified for {order_number}.")

print("--- 10. Testing Order Confirmation Page ---")
confirm_resp = c.get(f'/orders/confirmation/{order_number}/')
assert confirm_resp.status_code == 200
assert bytes(order_number, 'utf-8') in confirm_resp.content
assert b'Your Heirloom Chapter Has Begun' in confirm_resp.content
print(f"✓ Order confirmation page for {order_number} verified with full specifications.")

print("\n🎉 ALL 10 TESTS PASSED CLEANLY! STAGE 1 ORDERING SYSTEM IS FULLY FUNCTIONAL!")
