from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from orders.models import Order, OrderItem, OrderStatusHistory, ShippingAddress
from campaigns.models import JewelleryProduct
from store_admin.models import StoreSettings, EmailTemplate
from store_admin.utils import admin_required, role_required, log_audit, format_inr

@admin_required
def order_list_view(request):
    status_tab = request.GET.get('status', 'all')
    search_q = request.GET.get('q', '').strip()
    date_filter = request.GET.get('date', '')

    orders_qs = Order.objects.all().select_related('user', 'shipping_address')

    # Status filter tabs
    if status_tab == 'pending':
        orders_qs = orders_qs.filter(status__in=['new', 'awaiting_transfer'])
    elif status_tab == 'confirmed':
        orders_qs = orders_qs.filter(status='confirmed')
    elif status_tab == 'in_making':
        orders_qs = orders_qs.filter(status__in=['in_making', 'ready'])
    elif status_tab == 'shipped':
        orders_qs = orders_qs.filter(status='shipped')
    elif status_tab == 'delivered':
        orders_qs = orders_qs.filter(status='delivered')
    elif status_tab == 'cancelled':
        orders_qs = orders_qs.filter(status__in=['cancelled', 'returned'])

    # Search filter
    if search_q:
        orders_qs = orders_qs.filter(
            Q(order_number__icontains=search_q) |
            Q(customer_name__icontains=search_q) |
            Q(customer_phone__icontains=search_q) |
            Q(customer_email__icontains=search_q)
        )

    # Date filter
    now = timezone.now()
    if date_filter == 'today':
        orders_qs = orders_qs.filter(created_at__date=now.date())
    elif date_filter == 'week':
        orders_qs = orders_qs.filter(created_at__gte=now - timezone.timedelta(days=7))
    elif date_filter == 'month':
        orders_qs = orders_qs.filter(created_at__gte=now - timezone.timedelta(days=30))

    paginator = Paginator(orders_qs, 15)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    # Status counts for tab counters
    all_count = Order.objects.count()
    pending_count = Order.objects.filter(status__in=['new', 'awaiting_transfer']).count()
    confirmed_count = Order.objects.filter(status='confirmed').count()
    making_count = Order.objects.filter(status__in=['in_making', 'ready']).count()
    shipped_count = Order.objects.filter(status='shipped').count()
    delivered_count = Order.objects.filter(status='delivered').count()
    cancelled_count = Order.objects.filter(status__in=['cancelled', 'returned']).count()

    context = {
        'orders': orders_page,
        'status_tab': status_tab,
        'search_q': search_q,
        'date_filter': date_filter,
        'counts': {
            'all': all_count,
            'pending': pending_count,
            'confirmed': confirmed_count,
            'in_making': making_count,
            'shipped': shipped_count,
            'delivered': delivered_count,
            'cancelled': cancelled_count,
        },
        'active_nav': 'orders',
    }
    return render(request, 'store_admin/orders/list.html', context)


@admin_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    items = order.items.all().select_related('product')
    history = order.status_history.all().order_by('-created_at')

    status_options = [
        ('new', 'New Order (Received)'),
        ('confirmed', 'Confirmed & Verified'),
        ('in_making', 'In Making (Bench Karigar Crafting)'),
        ('ready', 'Ready for Armored Dispatch'),
        ('shipped', 'Shipped (In Armored Transit)'),
        ('delivered', 'Delivered (Signed by Patron)'),
        ('cancelled', 'Cancelled & Refunded'),
    ]

    context = {
        'order': order,
        'items': items,
        'history': history,
        'status_options': status_options,
        'active_nav': 'orders',
    }
    return render(request, 'store_admin/orders/detail.html', context)


@admin_required
def order_update_status_view(request, order_number):
    if request.method != 'POST':
        return redirect(f'/admin/orders/{order_number}/')

    order = get_object_or_404(Order, order_number=order_number)
    new_status = request.POST.get('status')
    comment = request.POST.get('comment', '').strip()
    tracking_number = request.POST.get('tracking_number', '').strip()
    notify_customer = request.POST.get('notify_customer') == 'on'

    old_status = order.status
    if new_status and new_status != old_status:
        order.status = new_status
        if tracking_number:
            order.bench_notes = f"{order.bench_notes}\n[Tracking: {tracking_number}]".strip()
        order.save(update_fields=['status', 'bench_notes', 'updated_at'])

        # Record timeline history
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            comment=comment or f"Status transitioned from {old_status} to {new_status}.",
            changed_by=request.user.first_name or request.user.username
        )

        log_audit(
            request, 'update', 'Order', order.id, order.order_number,
            f"Status changed from {old_status} to {new_status}. {comment}",
            {'status': old_status}, {'status': new_status}
        )

        messages.success(request, f"Order #{order.order_number} status updated to {new_status.title()}.")

    return redirect(f'/admin/orders/{order_number}/')


@admin_required
def order_invoice_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    items = order.items.all().select_related('product')
    store_settings = StoreSettings.get_settings()

    return render(request, 'store_admin/orders/invoice_print.html', {
        'order': order,
        'items': items,
        'store_settings': store_settings,
    })


@admin_required
def order_packing_slip_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    items = order.items.all().select_related('product')
    store_settings = StoreSettings.get_settings()

    return render(request, 'store_admin/orders/packing_slip.html', {
        'order': order,
        'items': items,
        'store_settings': store_settings,
    })
