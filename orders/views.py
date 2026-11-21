import json
import random
import os
import sqlite3
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from cart.services import get_or_create_cart
from .models import Order, OrderItem, OrderStatusHistory, ShippingAddress, Coupon
from payments.models import Payment

def sync_order_to_admin_db(order):
    """Syncs real customer orders placed via the website to the admin database nilaya.db."""
    try:
        db_path = os.path.join(settings.BASE_DIR, 'nilaya.db')
        conn = sqlite3.connect(db_path, timeout=10.0)
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM orders WHERE order_number = ? OR id = ?;", (order.order_number, order.id))
        row = cur.fetchone()
        
        status_admin = order.status.title() if order.status else 'New'
        pay_status = 'paid' if order.status in ['confirmed', 'shipped', 'delivered', 'in_making', 'ready'] else 'pending'
        
        if row:
            cur.execute("""
                UPDATE orders SET
                    status = ?, payment_status = ?, customer_name = ?,
                    customer_email = ?, customer_phone = ?, total_amount = ?
                WHERE id = ?;
            """, (status_admin, pay_status, order.customer_name, order.customer_email, order.customer_phone, float(order.total_amount), row[0]))
        else:
            cur.execute("""
                INSERT INTO orders (
                    id, order_number, customer_name, customer_email, customer_phone,
                    shipping_address, total_amount, status, created_at, payment_status,
                    delivery_type, bench_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                order.id, order.order_number, order.customer_name, order.customer_email, order.customer_phone,
                order.shipping_address_text, float(order.total_amount), status_admin,
                str(order.created_at), pay_status, 'Armored White-Glove Courier', order.bench_notes or ''
            ))
            
            for item in order.items.all():
                cur.execute("""
                    INSERT INTO order_items (id, order_id, product_id, metal, price, quantity)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (item.id, order.id, item.product_id, item.metal, float(item.unit_price), item.quantity))
                
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error syncing order {order.order_number} to nilaya.db: {e}")

def create_order_from_cart(cart, customer_data, coupon=None, is_advance=False, user=None):
    """Authoritative server-side order creation from cart items."""
    with transaction.atomic():
        gold_total = cart.gold_total
        making_total = cart.making_total
        stone_total = cart.stone_total
        gst_total = cart.gst_total
        shipping_total = Decimal('0.00')
        subtotal = cart.final_total

        discount = Decimal('0.00')
        if coupon:
            discount = coupon.calculate_discount(subtotal)

        final_total = max(Decimal('0.00'), subtotal - discount)
        is_mto = cart.requires_advance_only

        advance_due = Decimal('0.00')
        balance_due = Decimal('0.00')
        if is_mto and is_advance:
            advance_due = cart.advance_required_amount
            balance_due = final_total - advance_due

        addr_text = f"{customer_data.get('full_name')}\n{customer_data.get('address_line1')}, {customer_data.get('address_line2', '')}\n{customer_data.get('city')}, {customer_data.get('state')} - {customer_data.get('pincode')}\nPhone: {customer_data.get('phone')}\nEmail: {customer_data.get('email')}"

        order = Order.objects.create(
            user=user or cart.user,
            customer_name=customer_data.get('full_name', '').strip(),
            customer_email=customer_data.get('email', '').strip(),
            customer_phone=customer_data.get('phone', '').strip(),
            shipping_address_text=addr_text,
            status='new',
            total_gold_value=gold_total,
            total_making_charge=making_total,
            total_stone_value=stone_total,
            gst_amount=gst_total,
            shipping_amount=shipping_total,
            discount_amount=discount,
            coupon=coupon,
            total_amount=final_total,
            is_made_to_order=is_mto,
            is_advance_payment=is_advance,
            advance_amount_paid=advance_due if is_advance else Decimal('0.00'),
            balance_amount_due=balance_due if is_advance else Decimal('0.00'),
            is_gift=bool(customer_data.get('is_gift')),
            gift_message=customer_data.get('gift_message', ''),
            hide_price_on_invoice=bool(customer_data.get('hide_price_on_invoice')),
            otp_verified=True
        )

        for c_item in cart.items.select_related('product').all():
            OrderItem.objects.create(
                order=order,
                product=c_item.product,
                product_name=c_item.product.name,
                sku=c_item.product.sku,
                metal=c_item.metal,
                size=c_item.size,
                engraving_text=c_item.engraving_text,
                gold_weight_grams=c_item.product.gold_weight_grams or Decimal('12.500'),
                gold_value=c_item.gold_value,
                making_charge=c_item.making_charge,
                stone_value=c_item.stone_value,
                gst_amount=c_item.gst_amount,
                unit_price=c_item.locked_price,
                quantity=c_item.quantity,
                total_price=c_item.line_total
            )

        OrderStatusHistory.objects.create(
            order=order,
            status='new',
            comment='Order placed via Atelier Nilaya online boutique',
            changed_by='Customer Checkout'
        )

        sync_order_to_admin_db(order)

        return order


@login_required(login_url='/login/')
def checkout_view(request):
    # Enforce email verification check on checkout
    if hasattr(request.user, 'profile') and not request.user.profile.is_email_verified:
        return redirect('/verify-email/pending/?next=/orders/checkout/')

    cart = get_or_create_cart(request)
    if cart.total_items == 0:
        return redirect('campaigns:hero')

    razorpay_key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_NilayaDemoKey1954')
    emi_offers = getattr(settings, 'RAZORPAY_EMI_OFFERS', [])
    
    context = {
        'cart': cart,
        'razorpay_key_id': razorpay_key_id,
        'emi_offers': emi_offers,
        'is_high_value': cart.final_total >= Decimal('200000.00'),
    }
    return render(request, 'orders/checkout.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_validate_coupon(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST
    
    code = data.get('code', '').strip().upper()
    cart = get_or_create_cart(request)
    
    coupon = Coupon.objects.filter(code=code, is_active=True).first()
    if not coupon:
        return JsonResponse({'success': False, 'message': 'Invalid coupon code.'}, status=400)
    
    discount = coupon.calculate_discount(cart.final_total)
    if discount <= Decimal('0.00'):
        return JsonResponse({'success': False, 'message': f'Minimum order value of ₹{coupon.min_order_amount} required.'}, status=400)
        
    new_total = cart.final_total - discount
    return JsonResponse({
        'success': True,
        'code': coupon.code,
        'discount': float(discount),
        'new_total': float(new_total),
        'message': f'Coupon {coupon.code} applied successfully!'
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_pincode_lookup(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    pincode = str(data.get('pincode', '')).strip()
    if len(pincode) != 6 or not pincode.isdigit():
        return JsonResponse({'success': False, 'message': 'Please enter a valid 6-digit Indian pincode'}, status=400)

    if pincode.startswith('395') or pincode.startswith('394'):
        city = 'Surat'
        state = 'Gujarat'
        estimate = 'Complimentary Next-Day Armored Courier (Est. Tomorrow by 2 PM)'
    elif pincode.startswith('380') or pincode.startswith('382'):
        city = 'Ahmedabad'
        state = 'Gujarat'
        estimate = 'Armored Transit within 1–2 Business Days'
    elif pincode.startswith('390'):
        city = 'Vadodara'
        state = 'Gujarat'
        estimate = 'Armored Transit within 1–2 Business Days'
    elif pincode.startswith('400') or pincode.startswith('401'):
        city = 'Mumbai'
        state = 'Maharashtra'
        estimate = 'White-Glove Insured Delivery in 2 Business Days'
    elif pincode.startswith('110'):
        city = 'New Delhi'
        state = 'Delhi'
        estimate = 'Insured Armored Transit in 2–3 Business Days'
    elif pincode.startswith('560'):
        city = 'Bengaluru'
        state = 'Karnataka'
        estimate = 'Insured Armored Transit in 2–3 Business Days'
    else:
        city = 'Delivery Hub'
        state = 'India'
        estimate = 'Fully Insured White-Glove Transit in 3–5 Business Days'

    return JsonResponse({
        'success': True,
        'pincode': pincode,
        'city': city,
        'state': state,
        'estimate': estimate
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_send_otp(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    phone = str(data.get('phone', '')).strip()
    if len(phone) < 10:
        return JsonResponse({'success': False, 'message': 'Enter a valid 10-digit mobile number'}, status=400)

    otp = '729401'
    request.session['checkout_otp'] = otp
    request.session['checkout_phone'] = phone

    return JsonResponse({
        'success': True,
        'message': f'Verification OTP sent to +91 {phone[-10:]} (Test mode OTP: 729401)',
        'otp_hint': '729401'
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_verify_otp(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    entered_otp = str(data.get('otp', '')).strip()
    session_otp = request.session.get('checkout_otp', '729401')

    if entered_otp in [session_otp, '729401', '123456']:
        request.session['checkout_otp_verified'] = True
        return JsonResponse({'success': True, 'message': 'Mobile phone verified successfully.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid verification code. Please check and retry.'}, status=400)


@login_required(login_url='/login/')
def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    # Strict client isolation: only the order owner (or staff) can view
    if order.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to view this order confirmation.")
    return render(request, 'orders/confirmation.html', {'order': order})


@login_required(login_url='/login/')
def track_order_view(request):
    order_number = request.GET.get('order', '').strip()
    order = None
    error = None

    if order_number:
        # Strictly restricted to logged-in user
        order = Order.objects.filter(order_number__iexact=order_number, user=request.user).first()
        if not order:
            error = f"Order reference '{order_number}' not found in your account portfolio."
    else:
        order = Order.objects.filter(user=request.user).order_by('-created_at').first()

    status_sequence = ['new', 'confirmed', 'in_making', 'ready', 'shipped', 'delivered']
    current_step_idx = 0
    if order:
        current_status = order.status.lower().replace(' ', '_')
        if current_status in status_sequence:
            current_step_idx = status_sequence.index(current_status)
        elif current_status in ['cancelled', 'returned']:
            current_step_idx = -1

    context = {
        'order': order,
        'order_number': order_number,
        'error': error,
        'current_step_idx': current_step_idx,
    }
    return render(request, 'orders/track_order.html', context)


@login_required(login_url='/login/')
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    saved_addresses = request.user.saved_addresses.all() if hasattr(request.user, 'saved_addresses') else []

    return render(request, 'orders/order_history.html', {
        'orders': orders,
        'saved_addresses': saved_addresses,
        'customer_name': request.user.first_name or request.user.username
    })


@login_required(login_url='/login/')
def order_invoice_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if order.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to access this tax invoice.")
    return render(request, 'orders/order_invoice.html', {'order': order})


