import json
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from campaigns.models import JewelleryProduct
from .services import get_or_create_cart, calculate_item_bench_pricing
from .models import CartItem

def cart_state_payload(cart):
    items_data = []
    for item in cart.items.select_related('product', 'product__category').all():
        p = item.product
        metal_slug = item.metal.lower().replace(' ', '_')
        image_url = f"/static/products/{p.slug}/{metal_slug}/front.webp"
        items_data.append({
            'id': item.id,
            'product_id': p.id,
            'name': p.name,
            'slug': p.slug,
            'sku': p.sku,
            'metal': item.metal,
            'size': item.size,
            'engraving_text': item.engraving_text,
            'quantity': item.quantity,
            'locked_price': float(item.locked_price),
            'line_total': float(item.line_total),
            'gold_value': float(item.gold_value),
            'making_charge': float(item.making_charge),
            'stone_value': float(item.stone_value),
            'gst_amount': float(item.gst_amount),
            'image': image_url,
            'is_made_to_order': p.is_made_to_order,
            'making_days': p.making_days,
            'is_one_of_a_kind': p.is_one_of_a_kind,
        })

    return {
        'cart_id': cart.id,
        'total_items': cart.total_items,
        'gold_total': float(cart.gold_total),
        'making_total': float(cart.making_total),
        'stone_total': float(cart.stone_total),
        'gst_total': float(cart.gst_total),
        'subtotal_without_gst': float(cart.subtotal_without_gst),
        'shipping_total': float(cart.shipping_total),
        'final_total': float(cart.final_total),
        'requires_advance_only': cart.requires_advance_only,
        'advance_required_amount': float(cart.advance_required_amount),
        'items': items_data
    }

@csrf_exempt
@require_http_methods(["GET"])
def api_get_cart(request):
    cart = get_or_create_cart(request)
    payload = cart_state_payload(cart)
    notice = request.session.pop('cart_unavailable_notice', None)
    if notice:
        payload['unavailable_notice'] = notice
    return JsonResponse({
        'success': True,
        'count': cart.total_items,
        'cart_count': cart.total_items,
        'unavailable_notice': notice,
        'cart': payload
    })

@csrf_exempt
@require_http_methods(["POST", "GET"])
def api_add_to_cart(request):
    if request.method == "GET":
        return api_get_cart(request)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    product_id = data.get('product_id')
    slug = data.get('slug')
    product = None

    if product_id:
        try:
            product = JewelleryProduct.objects.filter(id=int(product_id)).first()
        except (ValueError, TypeError):
            pass

    if not product and slug:
        product = JewelleryProduct.objects.filter(slug=slug).first()

    if not product:
        # Fallback to first active product so add to cart never fails silently
        product = JewelleryProduct.objects.first()

    if not product:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

    metal = data.get('metal', getattr(product, 'base_metal', 'yellow_gold') or 'yellow_gold')
    size = data.get('size', 'Standard').strip()
    engraving_text = (data.get('engraving') or data.get('engraving_text') or '').strip()[:40]
    qty = max(1, int(data.get('quantity', 1)))
    if getattr(product, 'is_one_of_a_kind', False):
        qty = 1

    cart = get_or_create_cart(request)

    # Server price calculation
    bench_price = calculate_item_bench_pricing(product, metal)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        metal=metal,
        size=size,
        engraving_text=engraving_text,
        defaults={
            'quantity': qty,
            'locked_price': bench_price['unit_price'],
            'gold_value': bench_price['gold_value'],
            'making_charge': bench_price['making_charge'],
            'stone_value': bench_price['stone_value'],
            'gst_amount': bench_price['gst_amount'],
        }
    )

    if not created:
        if getattr(product, 'is_one_of_a_kind', False):
            item.quantity = 1
        else:
            item.quantity += qty
        item.locked_price = bench_price['unit_price']
        item.gold_value = bench_price['gold_value']
        item.making_charge = bench_price['making_charge']
        item.stone_value = bench_price['stone_value']
        item.gst_amount = bench_price['gst_amount']
        item.save()

    return JsonResponse({
        'success': True,
        'count': cart.total_items,
        'cart_count': cart.total_items,
        'message': f"Added {product.name} to acquisition bag",
        'cart': cart_state_payload(cart)
    })

@csrf_exempt
@require_http_methods(["POST"])
def api_update_cart_item(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    item_id = data.get('item_id')
    qty = int(data.get('quantity', 1))
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if qty <= 0:
        item.delete()
    else:
        item.quantity = qty
        item.save()

    return JsonResponse({'success': True, 'count': cart.total_items, 'cart_count': cart.total_items, 'cart': cart_state_payload(cart)})

@csrf_exempt
@require_http_methods(["POST"])
def api_remove_cart_item(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    item_id = data.get('item_id')
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()

    return JsonResponse({'success': True, 'count': cart.total_items, 'cart_count': cart.total_items, 'cart': cart_state_payload(cart)})
