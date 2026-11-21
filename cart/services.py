from decimal import Decimal, ROUND_HALF_UP
from campaigns.models import JewelleryProduct, GoldRate
from .models import Cart, CartItem

def calculate_item_bench_pricing(product: JewelleryProduct, metal: str):
    """
    Server-side authoritative jewellery pricing calculation.
    Never trusts client prices. Uses today's bullion rate from admin.
    Formula: (Gold Weight * Metal Rate) + Making Charge + Stone Value + 3% GST
    """
    rates = GoldRate.get_current_rates()
    metal = (metal or product.base_metal or 'yellow_gold').lower().replace(' ', '_')

    # Select base bullion rate per gram
    if 'platinum' in metal:
        gram_rate = rates.rate_platinum
    elif 'rose' in metal:
        gram_rate = rates.rate_18k * Decimal('1.04')
    elif 'silver' in metal:
        gram_rate = rates.rate_silver
    else:
        # Default 22k/24k gold
        if '24k' in str(product.metal_purity).lower():
            gram_rate = rates.rate_24k
        else:
            gram_rate = rates.rate_22k

    weight = product.gold_weight_grams or Decimal('12.500')
    gold_val = round(Decimal(weight) * Decimal(gram_rate), 2)

    # Making charges
    mc_type = product.making_charge_type or 'per_gram'
    mc_val = product.making_charge_value or Decimal('850.00')

    if mc_type == 'percentage':
        making_val = round(gold_val * (Decimal(mc_val) / Decimal('100.00')), 2)
    elif mc_type == 'flat':
        making_val = round(Decimal(mc_val), 2)
    else:  # per_gram
        making_val = round(Decimal(weight) * Decimal(mc_val), 2)

    stone_val = Decimal(product.stone_value or 0.00)

    taxable = gold_val + making_val + stone_val

    # If product has a predefined minimum price and calculated taxable is smaller, respect catalog floor
    if taxable < Decimal(product.price):
        diff = Decimal(product.price) - taxable
        making_val += diff
        taxable = gold_val + making_val + stone_val

    gst = round(taxable * Decimal('0.03'), 2)
    final_price = taxable + gst

    return {
        'gold_value': gold_val,
        'making_charge': making_val,
        'stone_value': stone_val,
        'gst_amount': gst,
        'unit_price': final_price,
        'gram_rate': gram_rate
    }


def get_or_create_cart(request):
    """
    Retrieves existing user or guest session cart; merges on login.
    Enforces no duplicates and caps one-of-a-kind pieces to 1.
    Flags any items that became unavailable during login.
    Safely merges guest carts across session key rotation.
    """
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    old_session_key = request.session.pop('guest_session_key', None)

    unavailable_items = []

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Merge any guest cart (checked against both current session key and rotated old key)
        guest_cart = None
        if old_session_key:
            guest_cart = Cart.objects.filter(session_key=old_session_key, user__isnull=True).first()
        if not guest_cart:
            guest_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()

        if guest_cart and guest_cart.id != cart.id:
            for g_item in guest_cart.items.select_related('product').all():
                prod = g_item.product
                # Check item availability
                if hasattr(prod, 'is_active') and not prod.is_active:
                    unavailable_items.append(prod.name)
                    g_item.delete()
                    continue

                existing = cart.items.filter(
                    product=prod,
                    metal=g_item.metal,
                    size=g_item.size,
                    engraving_text=g_item.engraving_text
                ).first()

                is_ooak = getattr(prod, 'is_one_of_a_kind', False) or getattr(prod, 'is_solitaire', False)

                if existing:
                    if is_ooak:
                        existing.quantity = 1
                    else:
                        existing.quantity += g_item.quantity
                    existing.save()
                    g_item.delete()
                else:
                    g_item.cart = cart
                    if is_ooak:
                        g_item.quantity = 1
                    g_item.save()
            guest_cart.delete()

        if unavailable_items:
            notice = f"The following piece(s) became unavailable while signing in: {', '.join(unavailable_items)}."
            request.session['cart_unavailable_notice'] = notice

        return cart
    else:
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart
