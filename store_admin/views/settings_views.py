from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from store_admin.models import (
    StoreSettings, ThemeSettings, HeaderMenuItem,
    FooterColumn, FooterLink, StoreShippingRule, EmailTemplate
)
from store_admin.utils import admin_required, log_audit

@admin_required
def settings_brand_view(request):
    settings = StoreSettings.get_settings()

    if request.method == 'POST':
        settings.store_name = request.POST.get('store_name', settings.store_name).strip()
        settings.brand_subname = request.POST.get('brand_subname', settings.brand_subname).strip()
        settings.tagline = request.POST.get('tagline', settings.tagline).strip()
        settings.provenance_city = request.POST.get('provenance_city', settings.provenance_city).strip()
        settings.monogram_text = request.POST.get('monogram_text', settings.monogram_text).strip()
        settings.contact_phone = request.POST.get('contact_phone', settings.contact_phone).strip()
        settings.contact_email = request.POST.get('contact_email', settings.contact_email).strip()
        settings.whatsapp_number = request.POST.get('whatsapp_number', settings.whatsapp_number).strip()
        settings.address = request.POST.get('address', settings.address).strip()
        settings.working_hours = request.POST.get('working_hours', settings.working_hours).strip()

        if 'logo_light' in request.FILES:
            settings.logo_light = request.FILES['logo_light']
        if 'logo_dark' in request.FILES:
            settings.logo_dark = request.FILES['logo_dark']
        if 'favicon' in request.FILES:
            settings.favicon = request.FILES['favicon']

        settings.save()
        log_audit(request, 'update', 'StoreSettings', settings.id, "Brand Identity", "Updated store name, logo & contact")
        messages.success(request, "Brand identity and concierge contact details saved.")
        return redirect('/admin/settings/brand/')

    return render(request, 'store_admin/settings/brand.html', {
        'settings': settings,
        'active_nav': 'settings',
        'active_subnav': 'brand',
    })


@admin_required
def settings_theme_view(request):
    theme = ThemeSettings.get_theme()

    if request.method == 'POST':
        theme.primary_color = request.POST.get('primary_color', theme.primary_color).strip()
        theme.primary_hover = request.POST.get('primary_hover', theme.primary_hover).strip()
        theme.accent_gold = request.POST.get('accent_gold', theme.accent_gold).strip()
        theme.accent_champagne = request.POST.get('accent_champagne', theme.accent_champagne).strip()
        theme.bg_canvas = request.POST.get('bg_canvas', theme.bg_canvas).strip()
        theme.surface_card = request.POST.get('surface_card', theme.surface_card).strip()
        theme.text_primary = request.POST.get('text_primary', theme.text_primary).strip()
        theme.text_muted = request.POST.get('text_muted', theme.text_muted).strip()
        theme.heading_font = request.POST.get('heading_font', theme.heading_font).strip()
        theme.body_font = request.POST.get('body_font', theme.body_font).strip()
        theme.button_radius = request.POST.get('button_radius', theme.button_radius).strip()
        theme.card_radius = request.POST.get('card_radius', theme.card_radius).strip()
        theme.enable_dark_accents = request.POST.get('enable_dark_accents') == 'on'
        theme.save()

        log_audit(request, 'update', 'ThemeSettings', theme.id, "Theme Tokens", f"Updated primary: {theme.primary_color}, gold: {theme.accent_gold}")
        messages.success(request, "Theme styling saved. Storefront live preview updated.")
        return redirect('/admin/settings/theme/')

    return render(request, 'store_admin/settings/theme.html', {
        'theme': theme,
        'active_nav': 'settings',
        'active_subnav': 'theme',
    })


@admin_required
def settings_header_footer_view(request):
    menus = HeaderMenuItem.objects.all().order_by('display_order')
    footer_cols = FooterColumn.objects.all().prefetch_related('links').order_by('display_order')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_menu_item':
            title = request.POST.get('title', '').strip()
            url = request.POST.get('url', '').strip()
            display_order = request.POST.get('display_order', menus.count() + 1)
            HeaderMenuItem.objects.create(
                title=title,
                url=url,
                display_order=int(display_order) if str(display_order).isdigit() else 1,
                is_active=True
            )
            messages.success(request, f"Menu item '{title}' added to navigation.")
            return redirect('/admin/settings/navigation/')

        elif action == 'delete_menu_item':
            item_id = request.POST.get('item_id')
            HeaderMenuItem.objects.filter(id=item_id).delete()
            messages.success(request, "Menu item removed.")
            return redirect('/admin/settings/navigation/')

    return render(request, 'store_admin/settings/navigation.html', {
        'menus': menus,
        'footer_cols': footer_cols,
        'active_nav': 'settings',
        'active_subnav': 'navigation',
    })


@admin_required
def settings_shipping_view(request):
    rules = StoreShippingRule.objects.all().order_by('display_order')
    settings = StoreSettings.get_settings()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'save_rules':
            for rule in rules:
                rule.price = Decimal(request.POST.get(f'price_{rule.id}', rule.price))
                rule.delivery_time_text = request.POST.get(f'time_{rule.id}', rule.delivery_time_text)
                rule.is_active = request.POST.get(f'active_{rule.id}') == 'on'
                rule.save()

            thresh = request.POST.get('free_shipping_threshold')
            if thresh:
                settings.free_shipping_threshold = Decimal(thresh)
                settings.save(update_fields=['free_shipping_threshold'])

            messages.success(request, "Shipping rates and thresholds saved.")
            return redirect('/admin/settings/shipping/')

    return render(request, 'store_admin/settings/shipping.html', {
        'rules': rules,
        'settings': settings,
        'active_nav': 'settings',
        'active_subnav': 'shipping',
    })


@admin_required
def settings_taxes_view(request):
    settings = StoreSettings.get_settings()

    if request.method == 'POST':
        settings.gst_rate_percent = Decimal(request.POST.get('gst_rate_percent', settings.gst_rate_percent))
        settings.company_legal_name = request.POST.get('company_legal_name', settings.company_legal_name).strip()
        settings.gstin_number = request.POST.get('gstin_number', settings.gstin_number).strip()
        settings.pan_number = request.POST.get('pan_number', settings.pan_number).strip()
        settings.invoice_prefix = request.POST.get('invoice_prefix', settings.invoice_prefix).strip()
        settings.bullion_notice_text = request.POST.get('bullion_notice_text', settings.bullion_notice_text).strip()
        settings.save()

        messages.success(request, "Tax, bullion policy and legal invoice settings saved.")
        return redirect('/admin/settings/taxes/')

    return render(request, 'store_admin/settings/taxes.html', {
        'settings': settings,
        'active_nav': 'settings',
        'active_subnav': 'taxes',
    })


@admin_required
def settings_emails_view(request):
    templates = EmailTemplate.objects.all().order_by('name')

    if request.method == 'POST':
        t_id = request.POST.get('template_id')
        t = get_object_or_404(EmailTemplate, id=t_id)
        t.subject = request.POST.get('subject', t.subject).strip()
        t.body_text = request.POST.get('body_text', t.body_text).strip()
        t.is_active = request.POST.get('is_active') == 'on'
        t.save()

        messages.success(request, f"Template '{t.name}' updated.")
        return redirect('/admin/settings/emails/')

    return render(request, 'store_admin/settings/emails.html', {
        'templates': templates,
        'active_nav': 'settings',
        'active_subnav': 'emails',
    })
