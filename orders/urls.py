from django.urls import path
from .views import (
    checkout_view,
    order_confirmation_view,
    track_order_view,
    order_history_view,
    api_validate_coupon,
    api_pincode_lookup,
    api_send_otp,
    api_verify_otp,
    order_invoice_view,
)

app_name = 'orders'

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('confirmation/<str:order_number>/', order_confirmation_view, name='confirmation'),
    path('order-confirmed/<str:order_number>/', order_confirmation_view, name='order_confirmed_alias'),
    path('invoice/<str:order_number>/', order_invoice_view, name='invoice'),
    path('track/', track_order_view, name='track'),
    path('history/', order_history_view, name='history'),
    path('my-orders/', order_history_view, name='my_orders'),
    path('api/coupon/validate/', api_validate_coupon, name='api_coupon_validate'),
    path('api/pincode/lookup/', api_pincode_lookup, name='api_pincode_lookup'),
    path('api/otp/send/', api_send_otp, name='api_otp_send'),
    path('api/otp/verify/', api_verify_otp, name='api_otp_verify'),
]
