from django.db import models
from django.conf import settings
from decimal import Decimal

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        user_str = self.user.username if self.user else f"Guest ({self.session_key[:8]})"
        return f"Cart #{self.id} for {user_str} ({self.total_items} pieces)"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def gold_total(self):
        return sum(item.gold_value * item.quantity for item in self.items.all())

    @property
    def making_total(self):
        return sum(item.making_charge * item.quantity for item in self.items.all())

    @property
    def stone_total(self):
        return sum(item.stone_value * item.quantity for item in self.items.all())

    @property
    def gst_total(self):
        return sum(item.gst_amount * item.quantity for item in self.items.all())

    @property
    def subtotal_without_gst(self):
        return self.gold_total + self.making_total + self.stone_total

    @property
    def shipping_total(self):
        return Decimal('0.00')  # Complimentary insured armored vault courier

    @property
    def final_total(self):
        return sum(item.locked_price * item.quantity for item in self.items.all())

    @property
    def requires_advance_only(self):
        # If any item is made to order
        return any(item.product.is_made_to_order for item in self.items.all())

    @property
    def advance_required_amount(self):
        adv = Decimal('0.00')
        for item in self.items.all():
            if item.product.is_made_to_order:
                adv_pct = (item.product.advance_payment_percentage or Decimal('25.00')) / Decimal('100.00')
                adv += (item.locked_price * item.quantity * adv_pct)
            else:
                adv += (item.locked_price * item.quantity)
        return round(adv, 2)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('campaigns.JewelleryProduct', on_delete=models.CASCADE)
    metal = models.CharField(max_length=50, default='yellow_gold')
    size = models.CharField(max_length=50, default='Standard', blank=True)
    engraving_text = models.CharField(max_length=50, blank=True, default='')
    quantity = models.PositiveIntegerField(default=1)
    
    # Server-calculated locked values at bench rates
    locked_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gold_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    making_charge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    stone_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.quantity}x {self.product.name} ({self.metal}) in Cart #{self.cart_id}"

    @property
    def line_total(self):
        return self.locked_price * self.quantity
