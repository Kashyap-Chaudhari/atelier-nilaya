from django.db import models
from django.utils import timezone
from campaigns.models import JewelleryProduct
from orders.models import Order

class StockReservation(models.Model):
    product = models.ForeignKey(JewelleryProduct, on_delete=models.CASCADE, related_name='reservations')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='reservations')
    session_key = models.CharField(max_length=100, blank=True, default='')
    quantity = models.PositiveIntegerField(default=1)
    expires_at = models.DateTimeField()
    is_released = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        return not self.is_released and self.expires_at > timezone.now()

    def __str__(self):
        status = "Active" if self.is_active() else "Expired/Released"
        return f"Lock ({self.quantity}) for {self.product.name} [{status}]"
