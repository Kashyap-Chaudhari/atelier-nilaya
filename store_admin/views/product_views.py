import csv
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils.text import slugify

from campaigns.models import JewelleryProduct, JewelleryCategory
from store_admin.utils import admin_required, role_required, log_audit, move_to_trash, format_inr

@admin_required
def product_list_view(request):
    search_q = request.GET.get('q', '').strip()
    cat_slug = request.GET.get('category', '')
    stock_status = request.GET.get('stock', '')
    sort_by = request.GET.get('sort', 'order')

    products = JewelleryProduct.objects.all().select_related('category')

    if search_q:
        products = products.filter(
            Q(name__icontains=search_q) |
            Q(sku__icontains=search_q) |
            Q(subcategory__icontains=search_q) |
            Q(tags__icontains=search_q)
        )

    if cat_slug:
        products = products.filter(category__slug=cat_slug)

    if stock_status == 'in_stock':
        products = products.filter(is_in_stock=True, stock_quantity__gt=0)
    elif stock_status == 'low_stock':
        products = products.filter(is_in_stock=True, stock_quantity__lte=3)
    elif stock_status == 'out_of_stock':
        products = products.filter(Q(is_in_stock=False) | Q(stock_quantity=0))

    if sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('display_order', '-id')

    paginator = Paginator(products, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = JewelleryCategory.objects.all()

    context = {
        'products': page_obj,
        'categories': categories,
        'search_q': search_q,
        'selected_cat': cat_slug,
        'selected_stock': stock_status,
        'selected_sort': sort_by,
        'total_count': products.count(),
        'active_nav': 'products',
    }
    return render(request, 'store_admin/products/list.html', context)


@admin_required
def product_create_view(request):
    categories = JewelleryCategory.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        sku = request.POST.get('sku', '').strip()
        category_id = request.POST.get('category')
        price = request.POST.get('price', '0')
        metal_purity = request.POST.get('metal_purity', '22K Gold')
        description = request.POST.get('description', '').strip()
        stock_quantity = request.POST.get('stock_quantity', '5')
        is_in_stock = request.POST.get('is_in_stock') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        is_bestseller = request.POST.get('is_bestseller') == 'on'
        gemstone_details = request.POST.get('gemstone_details', '').strip()
        gold_weight = request.POST.get('gold_weight_grams', '10.000')

        if not name or not category_id:
            messages.error(request, "Product name and category are required fields.")
            return render(request, 'store_admin/products/form.html', {'categories': categories, 'is_new': True})

        category = get_object_or_404(JewelleryCategory, id=category_id)
        slug = slugify(name)
        # Ensure slug uniqueness
        base_slug = slug
        c = 1
        while JewelleryProduct.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{c}"
            c += 1

        product = JewelleryProduct(
            name=name,
            slug=slug,
            sku=sku or f"NIL-{slug[:8].upper()}",
            category=category,
            price=Decimal(price),
            metal_purity=metal_purity,
            description=description,
            stock_quantity=int(stock_quantity) if stock_quantity.isdigit() else 1,
            is_in_stock=is_in_stock,
            is_featured=is_featured,
            is_bestseller=is_bestseller,
            gemstone_details=gemstone_details,
            gold_weight_grams=Decimal(gold_weight) if gold_weight else Decimal('10.000'),
        )

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()

        log_audit(request, 'create', 'JewelleryProduct', product.id, product.name, f"Created new product SKU: {product.sku}")
        messages.success(request, f"Heirloom piece '{product.name}' created successfully in {category.name}.")
        return redirect(f'/admin/products/{product.id}/edit/')

    return render(request, 'store_admin/products/form.html', {
        'categories': categories,
        'is_new': True,
        'active_nav': 'products',
    })


@admin_required
def product_edit_view(request, product_id):
    product = get_object_or_404(JewelleryProduct, id=product_id)
    categories = JewelleryCategory.objects.all()

    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.sku = request.POST.get('sku', '').strip()
        cat_id = request.POST.get('category')
        if cat_id:
            product.category = get_object_or_404(JewelleryCategory, id=cat_id)
        product.price = Decimal(request.POST.get('price', product.price))
        product.metal_purity = request.POST.get('metal_purity', product.metal_purity)
        product.description = request.POST.get('description', '').strip()
        product.short_description = request.POST.get('short_description', '').strip()
        product.eyebrow = request.POST.get('eyebrow', '').strip()
        product.gemstone_details = request.POST.get('gemstone_details', '').strip()
        product.stock_quantity = int(request.POST.get('stock_quantity', product.stock_quantity))
        product.is_in_stock = request.POST.get('is_in_stock') == 'on'
        product.is_featured = request.POST.get('is_featured') == 'on'
        product.is_bestseller = request.POST.get('is_bestseller') == 'on'
        product.is_made_to_order = request.POST.get('is_made_to_order') == 'on'
        product.huid_number = request.POST.get('huid_number', '').strip()

        weight_str = request.POST.get('gold_weight_grams')
        if weight_str:
            product.gold_weight_grams = Decimal(weight_str)

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()

        log_audit(request, 'update', 'JewelleryProduct', product.id, product.name, f"Updated specifications & price: ₹{product.price:,.0f}")
        messages.success(request, f"Changes saved for '{product.name}'. Live storefront updated.")
        return redirect(f'/admin/products/{product.id}/edit/')

    return render(request, 'store_admin/products/form.html', {
        'product': product,
        'categories': categories,
        'is_new': False,
        'active_nav': 'products',
    })


@admin_required
def product_duplicate_view(request, product_id):
    product = get_object_or_404(JewelleryProduct, id=product_id)
    new_product = JewelleryProduct.objects.get(id=product.id)
    new_product.pk = None
    new_product.id = None
    new_product.name = f"{product.name} (Copy)"
    new_product.slug = f"{product.slug}-copy"
    new_product.sku = f"{product.sku}-CPY"
    new_product.save()

    log_audit(request, 'create', 'JewelleryProduct', new_product.id, new_product.name, f"Duplicated from #{product.id}")
    messages.success(request, f"Duplicated '{product.name}'. You are now editing the duplicate.")
    return redirect(f'/admin/products/{new_product.id}/edit/')


@admin_required
def product_delete_view(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(JewelleryProduct, id=product_id)
        name = product.name
        move_to_trash(product, request.user)
        log_audit(request, 'delete', 'JewelleryProduct', product_id, name, "Archived piece to 30-day trash")
        messages.success(request, f"'{name}' moved to Trash. It can be restored within 30 days from Settings → Trash.")
    return redirect('/admin/products/')


@admin_required
def product_export_csv_view(request):
    """Exports entire product catalog into a clean CSV spreadsheet."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="atelier_nilaya_products.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'SKU', 'Category', 'Price (INR)', 'Purity', 'Gross Weight (g)', 'Stock', 'In Stock', 'Featured'])

    for p in JewelleryProduct.objects.all().select_related('category'):
        writer.writerow([
            p.id, p.name, p.sku, p.category.name, float(p.price),
            p.metal_purity, float(p.gold_weight_grams), p.stock_quantity,
            'Yes' if p.is_in_stock else 'No',
            'Yes' if p.is_featured else 'No'
        ])

    return response
