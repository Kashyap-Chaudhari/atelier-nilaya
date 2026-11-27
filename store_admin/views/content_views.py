from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from store_admin.models import (
    StoreSettings, HomepageSection, FeaturedEditBlock,
    FeaturedEditTile, PageContent
)
from campaigns.models import JewelleryCampaign
from store_admin.utils import admin_required, log_audit

@admin_required
def homepage_builder_view(request):
    store_settings = StoreSettings.get_settings()
    primary_campaign = JewelleryCampaign.objects.filter(is_active=True).first()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_curtains':
            store_settings.velvet_curtains_enabled = request.POST.get('velvet_curtains_enabled') == 'on'
            store_settings.save(update_fields=['velvet_curtains_enabled'])
            log_audit(request, 'update', 'StoreSettings', store_settings.id, "Velvet Curtains", f"Curtains enabled: {store_settings.velvet_curtains_enabled}")
            messages.success(request, "Velvet Curtains cover settings saved.")

        elif action == 'save_hero' and primary_campaign:
            primary_campaign.title = request.POST.get('title', primary_campaign.title).strip()
            primary_campaign.eyebrow = request.POST.get('eyebrow', primary_campaign.eyebrow).strip()
            primary_campaign.headline_sub = request.POST.get('headline_sub', primary_campaign.headline_sub).strip()
            primary_campaign.description = request.POST.get('description', primary_campaign.description).strip()
            primary_campaign.cta_text = request.POST.get('cta_text', primary_campaign.cta_text).strip()
            primary_campaign.cta_url = request.POST.get('cta_url', primary_campaign.cta_url).strip()
            primary_campaign.provenance_tag = request.POST.get('provenance_tag', primary_campaign.provenance_tag).strip()

            if 'poster_desktop' in request.FILES:
                primary_campaign.poster_desktop = request.FILES['poster_desktop']
            if 'video_desktop' in request.FILES:
                primary_campaign.video_desktop = request.FILES['video_desktop']

            primary_campaign.save()
            log_audit(request, 'update', 'JewelleryCampaign', primary_campaign.id, primary_campaign.title, "Updated hero campaign text & media")
            messages.success(request, f"Hero section '{primary_campaign.title}' updated. Live on storefront.")

        return redirect('/admin/content/homepage/')

    return render(request, 'store_admin/content/homepage_builder.html', {
        'store_settings': store_settings,
        'campaign': primary_campaign,
        'active_nav': 'content',
    })


@admin_required
def featured_edit_builder_view(request):
    block = FeaturedEditBlock.get_active()
    if not block:
        block = FeaturedEditBlock.objects.create(
            title='The Lapidary Benches',
            kicker='Curatorial Edit &bull; Autumn 2026',
            body='Over seven decades of uncompromised Surat stone cutting and sacred gold alloy metallurgy.',
            button_text='EXPLORE COLLECTION',
            button_link='/vault/'
        )

    tiles = block.tiles.all().order_by('display_order')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_main_block':
            block.title = request.POST.get('title', '').strip()
            block.kicker = request.POST.get('kicker', '').strip()
            block.body = request.POST.get('body', '').strip()
            block.button_text = request.POST.get('button_text', '').strip()
            block.button_link = request.POST.get('button_link', '').strip()
            block.is_active = request.POST.get('is_active') == 'on'

            if 'bg_image' in request.FILES:
                block.bg_image = request.FILES['bg_image']
            if 'hex_1_image' in request.FILES:
                block.hex_1_image = request.FILES['hex_1_image']
            if 'hex_2_image' in request.FILES:
                block.hex_2_image = request.FILES['hex_2_image']
            if 'hex_3_image' in request.FILES:
                block.hex_3_image = request.FILES['hex_3_image']

            block.save()
            log_audit(request, 'update', 'FeaturedEditBlock', block.id, block.title, "Updated Featured Edit headers & imagery")
            messages.success(request, "Featured Edit section saved successfully.")
            return redirect('/admin/content/featured-edit/')

        elif action == 'add_tile':
            title = request.POST.get('tile_title', '').strip()
            tile_type = request.POST.get('tile_type', 'product_grid')
            subtitle = request.POST.get('tile_subtitle', '').strip()
            copy = request.POST.get('tile_copy', '').strip()
            product_ids = request.POST.get('product_ids', '').strip()

            new_tile = FeaturedEditTile.objects.create(
                edit_block=block,
                tile_type=tile_type,
                title=title,
                subtitle=subtitle,
                copy=copy,
                product_ids=product_ids,
                display_order=tiles.count() + 1
            )
            if 'tile_image' in request.FILES:
                new_tile.image = request.FILES['tile_image']
                new_tile.save()

            messages.success(request, f"Tile '{title}' added to editorial grid.")
            return redirect('/admin/content/featured-edit/')

    return render(request, 'store_admin/content/featured_edit_builder.html', {
        'block': block,
        'tiles': tiles,
        'active_nav': 'content',
    })


@admin_required
def pages_list_view(request):
    pages = PageContent.objects.all().order_by('title')
    return render(request, 'store_admin/content/pages_list.html', {
        'pages': pages,
        'active_nav': 'content',
    })


@admin_required
def page_edit_view(request, slug):
    page = PageContent.objects.filter(slug=slug).first()
    if not page:
        page = PageContent.objects.create(
            title=slug.replace('-', ' ').title(),
            slug=slug,
            page_type='custom',
            body_html="<p>Enter page content here...</p>"
        )

    if request.method == 'POST':
        page.title = request.POST.get('title', page.title).strip()
        page.eyebrow = request.POST.get('eyebrow', page.eyebrow).strip()
        page.subtitle = request.POST.get('subtitle', page.subtitle).strip()
        page.body_html = request.POST.get('body_html', page.body_html)
        page.meta_title = request.POST.get('meta_title', '').strip()
        page.meta_description = request.POST.get('meta_description', '').strip()
        page.is_published = request.POST.get('is_published') == 'on'
        page.save()

        log_audit(request, 'update', 'PageContent', page.id, page.title, f"Updated page /{page.slug}/")
        messages.success(request, f"Page '{page.title}' updated successfully.")
        return redirect(f'/admin/content/pages/{page.slug}/')

    return render(request, 'store_admin/content/page_form.html', {
        'page': page,
        'active_nav': 'content',
    })
