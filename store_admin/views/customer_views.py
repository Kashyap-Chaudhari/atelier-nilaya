from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.contrib import messages

from orders.models import Order
from store_admin.utils import admin_required, log_audit, format_inr

@admin_required
def customer_list_view(request):
    search_q = request.GET.get('q', '').strip()
    customers_qs = User.objects.filter(is_staff=False).order_by('-date_joined')

    if search_q:
        customers_qs = customers_qs.filter(
            Q(username__icontains=search_q) |
            Q(email__icontains=search_q) |
            Q(first_name__icontains=search_q) |
            Q(last_name__icontains=search_q)
        )

    paginator = Paginator(customers_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store_admin/customers/list.html', {
        'customers': page_obj,
        'search_q': search_q,
        'total_count': customers_qs.count(),
        'active_nav': 'customers',
    })


@admin_required
def customer_detail_view(request, user_id):
    customer = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=customer).order_by('-created_at')
    total_spent = orders.exclude(status__in=['cancelled', 'returned']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'toggle_status':
            customer.is_active = not customer.is_active
            customer.save(update_fields=['is_active'])
            status_text = "unblocked" if customer.is_active else "blocked"
            log_audit(request, 'update', 'User', customer.id, customer.username, f"Customer account {status_text}")
            messages.success(request, f"Customer account {customer.username} has been {status_text}.")
            return redirect(f'/admin/customers/{customer.id}/')

    return render(request, 'store_admin/customers/detail.html', {
        'customer': customer,
        'orders': orders,
        'total_spent_inr': format_inr(total_spent),
        'active_nav': 'customers',
    })
