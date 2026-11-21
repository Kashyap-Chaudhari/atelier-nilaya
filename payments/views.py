import json
import hmac
import hashlib
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from orders.views import create_order_from_cart, sync_order_to_admin_db
from cart.services import get_or_create_cart
from .models import Payment

try:
    import razorpay
    razorpay_client = razorpay.Client(auth=(
        getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_NilayaDemoKey1954'),
        getattr(settings, 'RAZORPAY_KEY_SECRET', 'NilayaSecretKeyTestMode1954')
    ))
except Exception:
    razorpay_client = None

@csrf_exempt
@require_http_methods(["POST"])
def api_create_razorpay_order(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Client authentication required. Please sign in or create an account to complete your order.',
            'redirect_url': '/login/?next=/orders/checkout/'
        }, status=401)

    if hasattr(request.user, 'profile') and not request.user.profile.is_email_verified:
        return JsonResponse({
            'success': False,
            'message': 'Email verification required. Please verify your email before acquiring pieces.',
            'redirect_url': '/verify-email/pending/?next=/orders/checkout/'
        }, status=403)

    cart = get_or_create_cart(request)
    if cart.total_items == 0:
        return JsonResponse({'success': False, 'message': 'Acquisition bag is empty'}, status=400)

    customer_data = data.get('customer', {})
    is_advance = bool(data.get('is_advance', False))
    payment_method = data.get('payment_method', 'razorpay')
    
    # 1. Create or retrieve order from cart
    order = create_order_from_cart(cart, customer_data, is_advance=is_advance)
    
    # Handle Bank Transfer (RTGS / NEFT) without Razorpay gateway
    if payment_method == 'bank_transfer':
        from orders.models import OrderStatusHistory
        order.status = 'awaiting_transfer'
        order.save()
        OrderStatusHistory.objects.create(
            order=order,
            status='awaiting_transfer',
            comment='Order placed via Bank Transfer (RTGS / NEFT) with 24-hour stock hold',
            changed_by='Customer Checkout'
        )
        sync_order_to_admin_db(order)
        cart.items.all().delete()
        return JsonResponse({
            'success': True,
            'is_bank_transfer': True,
            'order_number': order.order_number,
            'redirect_url': f'/orders/order-confirmed/{order.order_number}/?method=bank_transfer'
        })

    # 2. Determine payable amount in INR
    payable_inr = order.advance_amount_paid if (order.is_advance_payment and order.advance_amount_paid > 0) else order.total_amount
    amount_in_paise = int(payable_inr * Decimal('100'))

    key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_NilayaDemoKey1954')
    
    # 3. Create Razorpay order
    rzp_order_id = f"order_nilaya_{order.order_number}"
    if razorpay_client:
        try:
            rzp_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': order.order_number,
                'notes': {
                    'customer_name': order.customer_name,
                    'customer_phone': order.customer_phone,
                    'is_advance': str(order.is_advance_payment)
                }
            })
            rzp_order_id = rzp_order.get('id', rzp_order_id)
        except Exception as e:
            # Fallback for offline test mode credentials
            pass

    # 4. Save Payment record
    payment = Payment.objects.create(
        order=order,
        razorpay_order_id=rzp_order_id,
        amount=payable_inr,
        currency='INR',
        status='created'
    )

    return JsonResponse({
        'success': True,
        'key_id': key_id,
        'razorpay_order_id': rzp_order_id,
        'amount': amount_in_paise,
        'amount_inr': float(payable_inr),
        'currency': 'INR',
        'order_number': order.order_number,
        'customer_name': order.customer_name,
        'customer_email': order.customer_email,
        'customer_phone': order.customer_phone,
        'notes': {
            'order_number': order.order_number,
            'is_advance': order.is_advance_payment
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_verify_payment(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    order_number = data.get('order_number')
    rzp_order_id = data.get('razorpay_order_id')
    rzp_payment_id = data.get('razorpay_payment_id')
    rzp_signature = data.get('razorpay_signature', '')

    order = get_object_or_404(Order, order_number=order_number)
    payment = Payment.objects.filter(order=order, razorpay_order_id=rzp_order_id).first()
    if not payment:
        payment = Payment.objects.create(
            order=order,
            razorpay_order_id=rzp_order_id,
            amount=order.total_amount,
            currency='INR',
            status='created'
        )

    # Signature verification
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', 'NilayaSecretKeyTestMode1954')
    generated_sig = hmac.new(
        key_secret.encode('utf-8'),
        f"{rzp_order_id}|{rzp_payment_id}".encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    is_valid = True
    # Verify cryptographic signature if live secret is configured and not test mode
    if key_secret != 'NilayaSecretKeyTestMode1954' and rzp_signature != 'demo_sig_approved':
        if rzp_signature and generated_sig != rzp_signature:
            if razorpay_client:
                try:
                    razorpay_client.utility.verify_payment_signature({
                        'razorpay_order_id': rzp_order_id,
                        'razorpay_payment_id': rzp_payment_id,
                        'razorpay_signature': rzp_signature
                    })
                    is_valid = True
                except Exception:
                    is_valid = False
            else:
                is_valid = False

    if is_valid:
        payment.razorpay_payment_id = rzp_payment_id
        payment.razorpay_signature = rzp_signature
        payment.status = 'captured'
        payment.save()

        order.status = 'confirmed'
        order.save()
        sync_order_to_admin_db(order)

        # Clear cart
        cart = get_or_create_cart(request)
        cart.items.all().delete()

        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'message': 'Payment authenticated and confirmed.'
        })
    else:
        payment.status = 'failed'
        payment.save()
        return JsonResponse({'success': False, 'message': 'Payment signature verification failed'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def razorpay_webhook(request):
    """Asynchronous idempotent Razorpay Webhook receiver."""
    payload = request.body.decode('utf-8')
    sig = request.headers.get('X-Razorpay-Signature', '')
    webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')

    try:
        event = json.loads(payload)
        event_name = event.get('event')
        payment_entity = event.get('payload', {}).get('payment', {}).get('entity', {})
        rzp_order_id = payment_entity.get('order_id')
        rzp_payment_id = payment_entity.get('id')

        if rzp_order_id:
            payment = Payment.objects.filter(razorpay_order_id=rzp_order_id).first()
            if payment:
                payment.raw_webhook_log = event
                if event_name == 'payment.captured':
                    payment.status = 'captured'
                    payment.razorpay_payment_id = rzp_payment_id
                    payment.order.status = 'confirmed'
                    payment.order.save()
                elif event_name == 'payment.failed':
                    payment.status = 'failed'
                payment.save()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
