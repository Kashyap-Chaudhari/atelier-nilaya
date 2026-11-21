from django.db import models
from orders.models import Order

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('manifested', 'Manifested (Vault Preparation)'),
        ('picked_up', 'In Armored Transit'),
        ('out_for_delivery', 'Out for White-Glove Delivery'),
        ('delivered', 'Delivered & Hallmarked'),
        ('failed', 'Delivery Attempt Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    courier_name = models.CharField(max_length=100, default='Sequel Armored Logistics')
    tracking_number = models.CharField(max_length=100, blank=True, default='')
    tracking_url = models.URLField(blank=True, default='')
    insured_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    requires_delivery_otp = models.BooleanField(default=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='manifested')
    dispatch_date = models.DateField(null=True, blank=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shipment for {self.order.order_number} ({self.courier_name}) — {self.status}"
