import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from campaigns.models import JewelleryProduct

class ShippingAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='saved_addresses'
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, default='Surat')
    state = models.CharField(max_length=100, default='Gujarat')
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} — {self.city}, {self.pincode}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=20,
        choices=[('percentage', 'Percentage (%)'), ('flat', 'Flat Amount (₹)')],
        default='percentage'
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Coupon {self.code} ({self.discount_value}{'%' if self.discount_type == 'percentage' else ' INR'})"

    def calculate_discount(self, order_amount: Decimal) -> Decimal:
        if not self.is_active or order_amount < self.min_order_amount:
            return Decimal('0.00')
        if self.discount_type == 'percentage':
            disc = order_amount * (self.discount_value / Decimal('100.00'))
            if self.max_discount_amount and disc > self.max_discount_amount:
                disc = self.max_discount_amount
            return round(disc, 2)
        else:
            return min(self.discount_value, order_amount)


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('awaiting_transfer', 'Awaiting transfer'),
        ('confirmed', 'Confirmed'),
        ('in_making', 'In making'),
        ('ready', 'Ready'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    order_number = models.CharField(max_length=60, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nilaya_orders'
    )
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.PROTECT, null=True, blank=True)
    shipping_address_text = models.TextField(help_text="Permanent address snapshot")
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new', db_index=True)
    
    # Financial breakdown
    total_gold_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_making_charge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_stone_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Bespoke & made to order handling
    is_made_to_order = models.BooleanField(default=False)
    is_advance_payment = models.BooleanField(default=False)
    advance_amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    balance_amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Gift options
    is_gift = models.BooleanField(default=False)
    gift_message = models.TextField(blank=True, default='')
    hide_price_on_invoice = models.BooleanField(default=False)
    
    # Verification & bench
    bench_notes = models.TextField(blank=True, default='')
    otp_code = models.CharField(max_length=6, blank=True, default='')
    otp_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} ({self.status}) — ₹{self.total_amount}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import datetime
            year = datetime.datetime.now().year
            rand_suffix = str(uuid.uuid4()).upper()[:6]
            self.order_number = f"NIL-{year}-{rand_suffix}"
        super().save(*args, **kwargs)

    @property
    def formatted_total(self):
        return f"₹{self.total_amount:,.2f}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(JewelleryProduct, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=60)
    metal = models.CharField(max_length=50)
    size = models.CharField(max_length=50, default='Standard')
    engraving_text = models.CharField(max_length=50, blank=True, default='')
    
    gold_weight_grams = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('0.000'))
    gold_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    making_charge = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    stone_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} in {self.order.order_number}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=30)
    comment = models.CharField(max_length=255, blank=True)
    changed_by = models.CharField(max_length=100, default='System')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.order_number} -> {self.status} at {self.created_at}"
