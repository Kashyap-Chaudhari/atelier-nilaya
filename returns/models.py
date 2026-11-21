from django.db import models
from orders.models import OrderItem

class ReturnRequest(models.Model):
    REASON_CHOICES = [
        ('size_exchange', 'Size Exchange Request'),
        ('bench_flaw', 'Quality or Setting Inspection'),
        ('different_piece', 'Exchange for Alternate Heirloom'),
        ('other', 'Other Request'),
    ]
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('under_inspection', 'Under Master Karigar Inspection'),
        ('approved', 'Approved'),
        ('rejected', 'Policy Non-Compliant'),
        ('completed', 'Completed'),
    ]

    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='return_requests')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    notes = models.TextField()
    photos = models.FileField(upload_to='returns/photos/', blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='requested')
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    refund_status = models.CharField(
        max_length=30,
        choices=[
            ('pending', 'Pending'),
            ('initiated', 'Initiated via Razorpay'),
            ('completed', 'Refund Settled'),
            ('not_applicable', 'Exchange Only')
        ],
        default='pending'
    )
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return #{self.id} for {self.order_item.product_name} ({self.status})"
