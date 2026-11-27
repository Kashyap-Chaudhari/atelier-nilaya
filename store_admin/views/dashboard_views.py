import json
from decimal import Decimal
from datetime import timedelta
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse

from orders.models import Order
from campaigns.models import JewelleryProduct, JewelleryCategory
from store_admin.models import StoreSettings, AdminAuditLog
from store_admin.utils import admin_required, format_inr

@admin_required
def dashboard_view(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # 1. Core Financial & Order Metrics
    all_orders = Order.objects.all()
    total_sales = all_orders.exclude(status__in=['cancelled', 'returned']).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    today_sales = all_orders.filter(created_at__gte=today_start).exclude(status__in=['cancelled', 'returned']).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')

    total_orders_count = all_orders.count()
    pending_orders_count = all_orders.filter(status__in=['new', 'awaiting_transfer', 'in_making']).count()
    delivered_orders_count = all_orders.filter(status='delivered').count()
    cancelled_orders_count = all_orders.filter(status__in=['cancelled', 'returned']).count()

    # 2. Inventory & Catalog Metrics
    total_products = JewelleryProduct.objects.count()
    in_stock_products = JewelleryProduct.objects.filter(is_in_stock=True, stock_quantity__gt=0).count()
    low_stock_products = JewelleryProduct.objects.filter(stock_quantity__lte=3, is_in_stock=True)
    low_stock_count = low_stock_products.count()
    total_categories = JewelleryCategory.objects.count()

    # 3. Customer Metrics
    total_customers = User.objects.filter(is_staff=False).count()

    # 4. Recent Activity
    recent_orders = all_orders.select_related('user').order_by('-created_at')[:8]
    recent_audit = AdminAuditLog.objects.order_by('-created_at')[:6]

    # 5. Last 7 Days Revenue Trend for Chart
    chart_labels = []
    chart_revenue = []
    for i in range(6, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        day_start = timezone.make_aware(timezone.datetime.combine(day_date, timezone.datetime.min.time()))
        day_end = timezone.make_aware(timezone.datetime.combine(day_date, timezone.datetime.max.time()))
        day_sum = all_orders.filter(created_at__range=(day_start, day_end)).exclude(status__in=['cancelled', 'returned']).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
        chart_labels.append(day_date.strftime('%a, %d %b'))
        chart_revenue.append(float(day_sum))

    # 6. Guided Setup Checklist
    store_settings = StoreSettings.get_settings()
    setup_checklist = [
        {'id': 'logo', 'title': 'Add Brand Logo & Favicon', 'done': bool(store_settings.logo_light or store_settings.favicon), 'url': '/admin/settings/brand/'},
        {'id': 'products', 'title': 'Review or Add Vault Pieces', 'done': total_products > 0, 'url': '/admin/products/'},
        {'id': 'shipping', 'title': 'Verify Delivery & Armored Rates', 'done': True, 'url': '/admin/settings/shipping/'},
        {'id': 'bullion', 'title': 'Configure Tax & Bullion Rate Note', 'done': bool(store_settings.gstin_number), 'url': '/admin/settings/taxes/'},
    ]
    completed_steps = sum(1 for item in setup_checklist if item['done'])

    context = {
        'total_sales_inr': format_inr(total_sales),
        'today_sales_inr': format_inr(today_sales),
        'total_orders_count': total_orders_count,
        'pending_orders_count': pending_orders_count,
        'delivered_orders_count': delivered_orders_count,
        'cancelled_orders_count': cancelled_orders_count,
        'total_products': total_products,
        'in_stock_products': in_stock_products,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products[:5],
        'total_categories': total_categories,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'recent_audit': recent_audit,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_revenue_json': json.dumps(chart_revenue),
        'setup_checklist': setup_checklist,
        'checklist_progress': int((completed_steps / len(setup_checklist)) * 100),
        'active_nav': 'dashboard',
    }
    return render(request, 'store_admin/dashboard.html', context)

@admin_required
def global_search_api(request):
    """Global search across products, orders, customers, and pages for Ctrl+K modal."""
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'results': []})

    results = []

    # Search Products
    products = JewelleryProduct.objects.filter(
        Q(name__icontains=q) | Q(sku__icontains=q) | Q(category__name__icontains=q)
    )[:5]
    for p in products:
        results.append({
            'type': 'Product',
            'title': p.name,
            'subtitle': f"SKU: {p.sku} • ₹{p.price:,.0f} • {p.metal_purity}",
            'url': f"/admin/products/{p.id}/edit/",
            'icon': 'gem'
        })

    # Search Orders
    orders = Order.objects.filter(
        Q(order_number__icontains=q) | Q(customer_name__icontains=q) | Q(customer_phone__icontains=q) | Q(customer_email__icontains=q)
    )[:5]
    for o in orders:
        results.append({
            'type': 'Order',
            'title': f"Order #{o.order_number}",
            'subtitle': f"{o.customer_name} • ₹{o.total_amount:,.0f} • {o.get_status_display()}",
            'url': f"/admin/orders/{o.order_number}/",
            'icon': 'package'
        })

    # Search Customers
    users = User.objects.filter(
        Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
    )[:4]
    for u in users:
        results.append({
            'type': 'Customer',
            'title': f"{u.get_full_name() or u.username}",
            'subtitle': u.email or "No email registered",
            'url': f"/admin/customers/{u.id}/",
            'icon': 'user'
        })

    return JsonResponse({'results': results})
