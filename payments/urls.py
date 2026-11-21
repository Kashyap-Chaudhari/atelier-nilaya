from django.urls import path
from .views import (
    api_create_razorpay_order,
    api_verify_payment,
    razorpay_webhook,
)

app_name = 'payments'

urlpatterns = [
    path('api/create-order/', api_create_razorpay_order, name='api_create_order'),
    path('api/order/create/', api_create_razorpay_order, name='api_order_create_alias'),
    path('api/verify-payment/', api_verify_payment, name='api_verify_payment'),
    path('api/verify/', api_verify_payment, name='api_verify_alias'),
    path('webhook/razorpay/', razorpay_webhook, name='webhook_razorpay'),
]
