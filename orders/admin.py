from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, ShippingAddress, Coupon

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'sku', 'metal', 'size', 'engraving_text', 'unit_price', 'quantity', 'total_price')

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'comment', 'changed_by', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'customer_phone', 'status', 'total_amount', 'is_made_to_order', 'created_at')
    list_filter = ('status', 'is_made_to_order', 'is_advance_payment', 'created_at')
    search_fields = ('order_number', 'customer_name', 'customer_phone', 'customer_email')
    inlines = [OrderItemInline, OrderStatusHistoryInline]

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_amount', 'is_active')

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'city', 'pincode', 'created_at')
