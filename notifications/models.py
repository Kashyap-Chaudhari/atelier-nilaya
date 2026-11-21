from django.db import models
from orders.models import Order

class NotificationLog(models.Model):
    CHANNEL_CHOICES = [
        ('whatsapp', 'Meta WhatsApp Cloud API'),
        ('email', 'Transactional Email (GST Invoice)'),
        ('sms', 'SMS OTP / Vault Gate'),
    ]
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    template_name = models.CharField(max_length=100)
    recipient = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message_payload = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.channel.upper()}] to {self.recipient} ({self.status})"
