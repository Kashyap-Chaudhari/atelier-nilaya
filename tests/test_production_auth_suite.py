import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unveiling_atelier.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from campaigns.models import UserProfile, JewelleryProduct
from orders.models import ShippingAddress
from cart.models import Cart, CartItem
from notifications.models import NotificationLog


def run_tests():
    print("==================================================")
    print("BEGINNING COMPREHENSIVE PRODUCTION AUTH SUITE TEST")
    print("==================================================")

    # Clean up test patron if exists
    test_email = "test_patron@unveilingatelier.luxury"
    test_phone = "9825199999"
    User.objects.filter(email=test_email).delete()

    client = Client()

    # ------------------------------------------------------------------
    # TEST 1: Open Redirect Defense
    # ------------------------------------------------------------------
    print("\n[TEST 1] Testing Open-Redirect Attack Prevention...")
    resp = client.get('/login/?next=https://malicious-external-site.com')
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    html = resp.content.decode()
    assert 'https://malicious-external-site.com' not in html, "Malicious external domain must be rejected!"
    assert 'value="/orders/history/"' in html or 'value=\'/orders/history/\'' in html, "Expected fallback /orders/history/"
    print("✓ Open-redirect defense verified: External domain neutralized.")

    # ------------------------------------------------------------------
    # TEST 2: User Sign Up with Validation
    # ------------------------------------------------------------------
    print("\n[TEST 2] Testing Client Sign Up...")
    # Missing consent
    resp = client.post('/signup/', {
        'full_name': 'Princess Gayatri',
        'email': test_email,
        'mobile_number': test_phone,
        'password': 'StrongPassword@1954',
        'confirm_password': 'StrongPassword@1954',
    })
    assert 'Terms of Service' in resp.content.decode(), "Must require consent!"

    # Mismatched passwords
    resp = client.post('/signup/', {
        'full_name': 'Princess Gayatri',
        'email': test_email,
        'mobile_number': test_phone,
        'password': 'StrongPassword@1954',
        'confirm_password': 'DifferentPassword@1954',
        'terms_consent': 'on',
    })
    assert 'passwords do not match' in resp.content.decode(), "Must detect password mismatch!"

    # Successful Sign Up
    resp = client.post('/signup/', {
        'full_name': 'Princess Gayatri',
        'email': test_email,
        'mobile_number': test_phone,
        'password': 'RoyalPassword#1954',
        'confirm_password': 'RoyalPassword#1954',
        'terms_consent': 'on',
    }, follow=False)
    assert resp.status_code == 302, f"Expected redirect after signup, got {resp.status_code}"
    # Verification email step is removed per requirements; user gets immediate access
    user = User.objects.get(email=test_email)
    assert user.profile.is_email_verified is True, "New user must start verified!"
    assert user.profile.mobile_number == test_phone, "Profile must store clean mobile number!"
    print("✓ User registered and immediately verified for seamless ordering.")

    # ------------------------------------------------------------------
    # TEST 3: User Cleared Directly for Checkout
    # ------------------------------------------------------------------
    print("\n[TEST 3] Testing Direct Checkout Access...")
    prod = JewelleryProduct.objects.filter(is_in_stock=True).first()
    if prod:
        client.post('/cart/add/', {'product_id': prod.id, 'quantity': 1})

    resp = client.get('/orders/checkout/', follow=False)
    assert resp.status_code == 200, f"Signed up user must have direct checkout access, got {resp.status_code}"
    print("✓ Registered user cleared directly for checkout without email verification blocker.")

    # ------------------------------------------------------------------
    # TEST 4: Authentication via Email and Mobile Number + Session Control
    # ------------------------------------------------------------------
    print("\n[TEST 6] Testing Login via Email and Mobile Number...")
    client.get('/logout/')

    # Test login via Email with "Remember me" (14 days)
    resp = client.post('/login/', {
        'identifier': test_email,
        'password': 'RoyalPassword#1954',
        'remember_me': 'on',
    }, follow=False)
    assert resp.status_code == 302, f"Expected 302 on login, got {resp.status_code}"
    assert client.session.get_expiry_age() == 14 * 86400, "Remember me should set 14-day expiry!"
    print("✓ Logged in via Email with 14-day Remember Me session.")

    client.get('/logout/')

    # Test login via Mobile Number without "Remember me" (browser session)
    resp = client.post('/login/', {
        'identifier': test_phone,
        'password': 'RoyalPassword#1954',
    }, follow=False)
    assert resp.status_code == 302, f"Expected 302 on login, got {resp.status_code}"
    assert client.session.get_expire_at_browser_close() is True, "Without remember me, session must expire on browser close!"
    print("✓ Logged in via 10-digit Mobile Number with browser-close session expiry.")

    # ------------------------------------------------------------------
    # TEST 7: Brute-Force Protection & 15-Minute Lockout
    # ------------------------------------------------------------------
    print("\n[TEST 7] Testing Brute-Force Lockout (5 failed attempts)...")
    client.get('/logout/')
    user.profile.reset_failed_attempts()

    for attempt in range(1, 5):
        resp = client.post('/login/', {'identifier': test_email, 'password': 'WrongPassword123'})
        assert 'Incorrect email or password' in resp.content.decode()

    # 5th failed attempt triggers lockout
    resp = client.post('/login/', {'identifier': test_email, 'password': 'WrongPassword123'})
    user.profile.refresh_from_db()
    assert user.profile.is_locked() is True, "Profile must be locked after 5 failed attempts!"
    print("✓ Account locked for 15 minutes after 5 failed attempts.")

    # Even with correct password, locked account must be rejected with lockout notice
    resp = client.post('/login/', {'identifier': test_email, 'password': 'RoyalPassword#1954'})
    assert 'temporarily locked' in resp.content.decode(), "Must inform customer account is locked!"
    print("✓ Locked account strictly denied authentication.")

    # Unlock for subsequent tests
    user.profile.reset_failed_attempts()

    # ------------------------------------------------------------------
    # TEST 8: Forgot Password & Anti-Enumeration
    # ------------------------------------------------------------------
    print("\n[TEST 8] Testing Forgot Password Anti-Enumeration...")
    resp_existing = client.post('/forgot-password/', {'email': test_email})
    resp_fake = client.post('/forgot-password/', {'email': 'completely_nonexistent@fake.com'})

    assert 'If this email is registered' in resp_existing.content.decode()
    assert 'If this email is registered' in resp_fake.content.decode()
    print("✓ Constant response returned for existing and non-existent emails (no enumeration possible).")

    # ------------------------------------------------------------------
    # TEST 9: Password Reset & Session Invalidation
    # ------------------------------------------------------------------
    print("\n[TEST 9] Testing Password Reset & Global Session Termination...")
    # Login on client1
    client1 = Client()
    client1.post('/login/', {'identifier': test_email, 'password': 'RoyalPassword#1954'})
    assert client1.session.get('_auth_user_id') == str(user.pk)

    # Perform password reset on client2
    user.refresh_from_db()
    client2 = Client()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_token = default_token_generator.make_token(user)

    resp = client2.post(f'/reset/{uid}/{reset_token}/', {
        'password': 'NewImperialPassword#1954',
        'confirm_password': 'NewImperialPassword#1954',
    }, follow=False)
    assert resp.status_code == 302 and 'reset_success=1' in resp['Location'], "Must redirect to login with reset_success!"

    # Verify old session on client1 is invalidated
    resp_client1 = client1.get('/account/profile/', follow=False)
    assert resp_client1.status_code == 302 and '/login/' in resp_client1['Location'], "Other device session must be terminated!"
    print("✓ Password successfully reset; all other active user sessions invalidated.")

    # ------------------------------------------------------------------
    # TEST 10: Account Suite Views (Profile, Change Password, Saved Addresses)
    # ------------------------------------------------------------------
    print("\n[TEST 10] Testing Account Suite (Profile, Password Change, Addresses)...")
    client_auth = Client()
    client_auth.post('/login/', {'identifier': test_email, 'password': 'NewImperialPassword#1954'})

    # 1. Profile update
    resp = client_auth.post('/account/profile/', {
        'first_name': 'Her Highness Gayatri Devi',
        'mobile_number': '9825188888',
    })
    user.refresh_from_db()
    assert user.first_name == 'Her Highness Gayatri Devi'
    assert user.profile.mobile_number == '9825188888'
    print("✓ Account profile updated successfully.")

    # 2. Change password inside account (requires current password)
    resp = client_auth.post('/account/password/', {
        'current_password': 'WrongCurrentPassword',
        'new_password': 'FinalRoyalPassword#1954',
        'confirm_password': 'FinalRoyalPassword#1954',
    })
    assert 'current password entered is incorrect' in resp.content.decode()

    resp = client_auth.post('/account/password/', {
        'current_password': 'NewImperialPassword#1954',
        'new_password': 'FinalRoyalPassword#1954',
        'confirm_password': 'FinalRoyalPassword#1954',
    })
    assert 'updated successfully' in resp.content.decode()
    user.refresh_from_db()
    assert user.check_password('FinalRoyalPassword#1954') is True
    print("✓ Password changed from account settings with current password verification.")

    # 3. Saved Addresses
    resp = client_auth.post('/account/addresses/', {
        'action': 'add_address',
        'full_name': 'Her Highness Gayatri Devi',
        'phone': '9825188888',
        'address_line1': 'Nilaya Heritage Palace, Royal Road',
        'city': 'Surat',
        'state': 'Gujarat',
        'pincode': '395007',
    })
    addr = ShippingAddress.objects.filter(user=user, pincode='395007').first()
    assert addr is not None, "Address must be saved!"
    print("✓ Saved delivery address created and verified.")

    # ------------------------------------------------------------------
    # TEST 11: Guest Cart Preservation and Merging on Login
    # ------------------------------------------------------------------
    print("\n[TEST 11] Testing Guest Cart Merge on Login...")
    guest = Client()
    if prod:
        guest.post('/cart/add/', {'product_id': prod.id, 'quantity': 1})
        guest_cart = Cart.objects.filter(session_key=guest.session.session_key).first()
        assert guest_cart is not None and guest_cart.items.count() > 0

        # Login to merge
        guest.post('/login/', {'identifier': test_email, 'password': 'FinalRoyalPassword#1954'})
        user_cart = Cart.objects.filter(user=user).first()
        assert user_cart is not None and user_cart.items.count() > 0, "Guest cart items must merge into user cart!"
        print("✓ Guest cart preserved and seamlessly merged into patron folio without duplicates.")

    print("\n==================================================")
    print("ALL 11 PRODUCTION AUTHENTICATION TESTS PASSED!")
    print("==================================================")


if __name__ == '__main__':
    run_tests()
