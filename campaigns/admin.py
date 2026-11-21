from django.contrib import admin
from django.utils.html import format_html
from .models import JewelleryCampaign, JewelleryCategory, JewelleryProduct

@admin.register(JewelleryCampaign)
class JewelleryCampaignAdmin(admin.ModelAdmin):
    list_display = (
        'formatted_order',
        'title',
        'eyebrow',
        'theme_accent',
        'composition_style',
        'display_order',
        'is_active',
        'media_preview',
        'updated_at',
    )
    list_display_links = ('formatted_order', 'title')
    list_editable = ('display_order', 'is_active', 'theme_accent')
    list_filter = ('is_active', 'theme_accent', 'composition_style', 'created_at')
    search_fields = ('title', 'eyebrow', 'headline_sub', 'description', 'curator_note')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('display_order', 'id')

    fieldsets = (
        ('Collection Identity', {
            'fields': (
                'title',
                'slug',
                'eyebrow',
                'headline_sub',
                'description',
            )
        }),
        ('Visual Presentation & Architecture', {
            'fields': (
                'theme_accent',
                'composition_style',
                'curator_note',
                'provenance_tag',
            )
        }),
        ('Cinematic Video Assets', {
            'fields': (
                'video_desktop',
                'video_desktop_preview',
                'video_mobile',
                'video_mobile_preview',
            )
        }),
        ('Editorial Poster Photography', {
            'fields': (
                'poster_desktop',
                'poster_desktop_preview',
                'poster_mobile',
                'poster_mobile_preview',
            )
        }),
        ('Call To Action & Visibility', {
            'fields': (
                'cta_text',
                'cta_url',
                'display_order',
                'is_active',
            )
        }),
    )

    readonly_fields = (
        'media_preview',
        'video_desktop_preview',
        'video_mobile_preview',
        'poster_desktop_preview',
        'poster_mobile_preview',
    )

    def media_preview(self, obj):
        if obj.poster_desktop:
            return format_html(
                '<div style="display:flex; align-items:center; gap:8px;">'
                '<img src="{}" style="width:64px; height:42px; object-fit:cover; border-radius:3px; border:1px solid #AD9161;" />'
                '<span style="font-size:11px; color:#666;">{}</span>'
                '</div>',
                obj.poster_desktop.url,
                "✓ Video" if obj.video_desktop else "No Video"
            )
        return format_html('<span style="color:#999;">No poster</span>')
    media_preview.short_description = 'Media Preview'

    def video_desktop_preview(self, obj):
        if obj.video_desktop:
            return format_html(
                '<video src="{}" controls style="max-width:320px; max-height:180px; border:1px solid #ccc; border-radius:4px;" preload="metadata"></video>',
                obj.video_desktop.url
            )
        return "Upload a desktop video file to preview"
    video_desktop_preview.short_description = 'Desktop Video Preview'

    def video_mobile_preview(self, obj):
        if obj.video_mobile:
            return format_html(
                '<video src="{}" controls style="max-width:200px; max-height:280px; border:1px solid #ccc; border-radius:4px;" preload="metadata"></video>',
                obj.video_mobile.url
            )
        return "Optional. Falls back to desktop video if empty."
    video_mobile_preview.short_description = 'Mobile Video Preview'

    def poster_desktop_preview(self, obj):
        if obj.poster_desktop:
            return format_html(
                '<img src="{}" style="max-width:320px; max-height:180px; object-fit:cover; border-radius:4px; border:1px solid #AD9161;" />',
                obj.poster_desktop.url
            )
        return "Upload a poster to preview"
    poster_desktop_preview.short_description = 'Desktop Poster Preview'

    def poster_mobile_preview(self, obj):
        if obj.poster_mobile:
            return format_html(
                '<img src="{}" style="max-width:200px; max-height:280px; object-fit:cover; border-radius:4px; border:1px solid #AD9161;" />',
                obj.poster_mobile.url
            )
        return "Optional. Falls back to desktop poster if empty."
    poster_mobile_preview.short_description = 'Mobile Poster Preview'


@admin.register(JewelleryCategory)
class JewelleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('display_order', 'name', 'subtitle', 'product_count_display', 'is_active')
    list_display_links = ('name',)
    list_editable = ('display_order', 'is_active')
    search_fields = ('name', 'subtitle', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def product_count_display(self, obj):
        return f"{obj.product_count} products"
    product_count_display.short_description = 'Products'


@admin.register(JewelleryProduct)
class JewelleryProductAdmin(admin.ModelAdmin):
    list_display = ('image_thumb', 'name', 'category', 'sku', 'formatted_price', 'metal_purity', 'is_featured', 'is_in_stock')
    list_display_links = ('name',)
    list_filter = ('category', 'metal_purity', 'is_featured', 'is_bestseller', 'is_in_stock')
    search_fields = ('name', 'sku', 'eyebrow', 'description', 'gemstone_details')
    list_editable = ('is_featured', 'is_in_stock')
    prepopulated_fields = {'slug': ('name',)}

    def image_thumb(self, obj):
        url = obj.display_image
        if url:
            return format_html('<img src="{}" style="width:40px; height:40px; object-fit:cover; border-radius:3px; border:1px solid #682D3C;" />', url)
        return 'No Image'
    image_thumb.short_description = 'Preview'
