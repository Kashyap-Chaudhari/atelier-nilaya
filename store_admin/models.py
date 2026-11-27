import os
import json
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


# ==============================================================================
# 1. ADMIN USER & ROLE-BASED ACCESS CONTROL (RBAC)
# ==============================================================================
class AdminProfile(models.Model):
    ROLE_SUPER_ADMIN = 'super_admin'
    ROLE_PRODUCT_MGR = 'product_manager'
    ROLE_ORDER_MGR = 'order_manager'
    ROLE_CONTENT_MGR = 'content_manager'
    ROLE_SUPPORT_MGR = 'support_manager'

    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, 'Super Admin (Full Sovereign Access)'),
        (ROLE_PRODUCT_MGR, 'Product Manager (Catalog, Images, 360, Inventory)'),
        (ROLE_ORDER_MGR, 'Order Manager (Orders, Invoices, Shipping, Refunds)'),
        (ROLE_CONTENT_MGR, 'Content Manager (Homepage, Banners, Pages, Theme)'),
        (ROLE_SUPPORT_MGR, 'Support Manager (Customers, Orders, Reviews)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=ROLE_SUPER_ADMIN)
    display_title = models.CharField(max_length=100, default='Principal Curator')
    phone = models.CharField(max_length=32, blank=True)
    avatar = models.ImageField(upload_to='admin/avatars/', blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    is_active_staff = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def has_module_access(self, module_name):
        if self.role == self.ROLE_SUPER_ADMIN:
            return True
        role_map = {
            self.ROLE_PRODUCT_MGR: ['products', 'categories', 'inventory', 'media'],
            self.ROLE_ORDER_MGR: ['orders', 'customers', 'shipping', 'payments'],
            self.ROLE_CONTENT_MGR: ['content', 'homepage', 'featured_edit', 'pages', 'settings', 'media'],
            self.ROLE_SUPPORT_MGR: ['orders', 'customers', 'reviews'],
        }
        allowed = role_map.get(self.role, [])
        return module_name in allowed


# ==============================================================================
# 2. STORE-WIDE SETTINGS (BRAND, THEME, HEADER, FOOTER, COMMERCE)
# ==============================================================================
class StoreSettings(models.Model):
    """Singleton model holding global store configuration."""
    singleton_id = models.IntegerField(default=1, unique=True)

    # Brand Identity
    store_name = models.CharField(max_length=150, default='Atelier Nilaya')
    brand_subname = models.CharField(max_length=150, default='Haute Joaillerie')
    tagline = models.CharField(max_length=255, default='The Art of Becoming Heirloom')
    provenance_city = models.CharField(max_length=100, default='Surat &bull; Est. 1954')
    monogram_text = models.CharField(max_length=10, default='✦')
    logo_light = models.ImageField(upload_to='settings/logos/', blank=True, null=True)
    logo_dark = models.ImageField(upload_to='settings/logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/logos/', blank=True, null=True)

    # Contact & Concierge
    address = models.TextField(default='Atelier Nilaya, Nanpura Heritage District, Surat, Gujarat 395001')
    contact_phone = models.CharField(max_length=50, default='+91 261 247 1954')
    contact_email = models.EmailField(default='concierge@ateliernilaya.com')
    whatsapp_number = models.CharField(max_length=30, default='+919825100000')
    working_hours = models.CharField(max_length=150, default='Monday – Saturday: 11:00 AM – 7:30 PM (By Private Appointment)')

    # Commercial, Taxes & Bullion
    currency_symbol = models.CharField(max_length=10, default='₹')
    currency_code = models.CharField(max_length=10, default='INR')
    gst_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    company_legal_name = models.CharField(max_length=200, default='Atelier Nilaya Private Limited')
    gstin_number = models.CharField(max_length=50, default='24AABCA1234F1Z8')
    pan_number = models.CharField(max_length=30, default='AABCA1234F')
    invoice_prefix = models.CharField(max_length=20, default='AN-2026-')
    bullion_notice_text = models.CharField(max_length=255, default='Transparent benchmark bullion rates locked at checkout')
    free_shipping_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=50000.00)

    # Global Feature Toggles
    maintenance_mode = models.BooleanField(default=False)
    maintenance_title = models.CharField(max_length=200, default='The Atelier Is In Private Preparation')
    maintenance_message = models.TextField(default='Our master goldsmiths are currently curating new archival masterpieces. We will unveil shortly.')
    velvet_curtains_enabled = models.BooleanField(default=True)
    whatsapp_floating_enabled = models.BooleanField(default=True)
    cookie_banner_enabled = models.BooleanField(default=False)

    # Announcement & Badges
    announcement_text = models.CharField(max_length=255, default='Armored white-glove insured delivery across India &bull; BIS 916 Hallmarked')
    announcement_link = models.CharField(max_length=255, default='/vault/')
    announcement_active = models.BooleanField(default=True)

    trust_badge_1_title = models.CharField(max_length=100, default='Armored Insured Delivery')
    trust_badge_1_desc = models.CharField(max_length=200, default='Armored white-glove transit with full insurance across India.')
    trust_badge_2_title = models.CharField(max_length=100, default='BIS 916 & Guild Certified')
    trust_badge_2_desc = models.CharField(max_length=200, default='Tamper-proof digital hallmark registry and certificate per piece.')

    # 404 Error Page Customization
    error_404_title = models.CharField(max_length=150, default='Heirloom Not Found')
    error_404_message = models.TextField(default='The royal creation you are seeking may have retired to our private vault or been acquired.')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Store Settings'
        verbose_name_plural = 'Store Settings'

    def __str__(self):
        return f"{self.store_name} Settings"

    @classmethod
    def get_settings(cls):
        try:
            obj, _ = cls.objects.get_or_create(singleton_id=1)
            return obj
        except Exception:
            return cls(singleton_id=1, store_name='Atelier Nilaya', tagline='Haute Joaillerie & High Art')


class ThemeSettings(models.Model):
    """Storefront design tokens editable directly from admin."""
    singleton_id = models.IntegerField(default=1, unique=True)

    primary_color = models.CharField(max_length=30, default='#642D3B')  # Burgundy / Wine
    primary_hover = models.CharField(max_length=30, default='#7D3749')
    accent_gold = models.CharField(max_length=30, default='#B8893B')    # Gold
    accent_champagne = models.CharField(max_length=30, default='#D7C19A')
    bg_canvas = models.CharField(max_length=30, default='#FAF7F2')       # Soft Ivory
    surface_card = models.CharField(max_length=30, default='#FFFFFF')    # Pure White
    text_primary = models.CharField(max_length=30, default='#2B1A1F')    # Deep Bronze
    text_muted = models.CharField(max_length=30, default='#705953')      # Muted Warm Grey
    border_subtle = models.CharField(max_length=50, default='rgba(100, 45, 59, 0.16)')

    heading_font = models.CharField(max_length=100, default="'Cormorant Garamond', Georgia, serif")
    body_font = models.CharField(max_length=100, default="'Montserrat', -apple-system, sans-serif")
    button_radius = models.CharField(max_length=20, default='4px')
    card_radius = models.CharField(max_length=20, default='8px')
    enable_dark_accents = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Theme Settings'
        verbose_name_plural = 'Theme Settings'

    def __str__(self):
        return "Storefront Theme Tokens"

    @classmethod
    def get_theme(cls):
        try:
            obj, _ = cls.objects.get_or_create(singleton_id=1)
            return obj
        except Exception:
            return cls(singleton_id=1)


# ==============================================================================
# 3. HEADER & FOOTER NAVIGATION BUILDER
# ==============================================================================
class HeaderMenuItem(models.Model):
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_dropdown = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_external = models.BooleanField(default=False)
    badge_label = models.CharField(max_length=30, blank=True)
    thumbnail = models.ImageField(upload_to='navigation/menus/', blank=True, null=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Header Menu Item'
        verbose_name_plural = 'Header Menu Items'

    def __str__(self):
        return f"{self.title} ({self.url})"


class FooterColumn(models.Model):
    title = models.CharField(max_length=100)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Footer Column'
        verbose_name_plural = 'Footer Columns'

    def __str__(self):
        return self.title


class FooterLink(models.Model):
    column = models.ForeignKey(FooterColumn, on_delete=models.CASCADE, related_name='links')
    label = models.CharField(max_length=100)
    url = models.CharField(max_length=255)
    display_order = models.PositiveIntegerField(default=0)
    is_external = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Footer Link'
        verbose_name_plural = 'Footer Links'

    def __str__(self):
        return f"{self.label} -> {self.url}"


# ==============================================================================
# 4. HOMEPAGE SECTIONS & FEATURED EDIT BUILDER
# ==============================================================================
class HomepageSection(models.Model):
    SECTION_TYPES = [
        ('curtains', 'Intro Velvet Curtains'),
        ('hero', 'Main Cinematic Hero & Story Rail'),
        ('turntable_360', 'Interactive 360° Turntable Banner'),
        ('philosophy', 'Curatorial Philosophy Manifesto'),
        ('featured_edit', 'Featured Edit (Faded Band & Hexagonal Grid)'),
        ('chapters', 'Four Master Chapters (Velvet Tray Story)'),
        ('sketchbook', 'Master Karigar Sketchbook'),
        ('family_album', 'Generations of Surat Goldsmiths'),
        ('appointment', 'Private Viewing Appointment Concierge'),
        ('newsletter', 'Private Salon Newsletter Signup'),
        ('custom_banner', 'Custom Promotional Editorial Banner'),
    ]

    section_type = models.CharField(max_length=40, choices=SECTION_TYPES, unique=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    kicker = models.CharField(max_length=100, blank=True)
    content_payload = models.JSONField(default=dict, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    draft_status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft (Unpublished)'), ('published', 'Published (Live)'), ('scheduled', 'Scheduled')],
        default='published'
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Homepage Section'
        verbose_name_plural = 'Homepage Sections'

    def __str__(self):
        return f"{self.get_section_type_display()} - {self.title}"


class FeaturedEditBlock(models.Model):
    """Controls the mid-page Featured Edit Section."""
    title = models.CharField(max_length=200, default='The Lapidary Benches')
    kicker = models.CharField(max_length=100, default='Curatorial Edit &bull; Autumn 2026')
    body = models.TextField(default='Over seven decades of uncompromised Surat stone cutting and sacred gold alloy metallurgy.')
    button_text = models.CharField(max_length=50, default='EXPLORE COLLECTION')
    button_link = models.CharField(max_length=200, default='/vault/')
    bg_image = models.ImageField(upload_to='featured_edit/', blank=True, null=True)

    hex_1_image = models.ImageField(upload_to='featured_edit/', blank=True, null=True)
    hex_1_alt = models.CharField(max_length=150, default='Atelier Solitaire Ring')
    hex_2_image = models.ImageField(upload_to='featured_edit/', blank=True, null=True)
    hex_2_alt = models.CharField(max_length=150, default='Diamond Chandelier Suite')
    hex_3_image = models.ImageField(upload_to='featured_edit/', blank=True, null=True)
    hex_3_alt = models.CharField(max_length=150, default='Royal Kundan Necklace')

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Featured Edit Section'
        verbose_name_plural = 'Featured Edit Sections'

    def __str__(self):
        return f"Featured Edit: {self.title}"

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first()


class FeaturedEditTile(models.Model):
    TILE_TYPES = [
        ('product_grid', 'Product Group Grid (Select Pieces)'),
        ('editorial_quote', 'Editorial Karigar Quote'),
        ('large_feature', 'Large Photography Feature'),
    ]

    edit_block = models.ForeignKey(FeaturedEditBlock, on_delete=models.CASCADE, related_name='tiles', null=True, blank=True)
    tile_type = models.CharField(max_length=30, choices=TILE_TYPES, default='product_grid')
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=200, blank=True)
    copy = models.TextField(blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=200, blank=True)
    product_ids = models.CharField(max_length=255, blank=True, help_text='Comma-separated product IDs (e.g. 1, 4, 7)')
    image = models.ImageField(upload_to='featured_edit/tiles/', blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Featured Edit Tile'
        verbose_name_plural = 'Featured Edit Tiles'

    def __str__(self):
        return f"{self.title} ({self.get_tile_type_display()})"


# ==============================================================================
# 5. CUSTOM PAGES & STATUTORY LEGAL POLICIES
# ==============================================================================
class PageContent(models.Model):
    PAGE_TYPES = [
        ('about', 'About Us & Heritage Story'),
        ('privacy', 'Privacy Policy'),
        ('terms', 'Terms of Provenance & Sales'),
        ('shipping', 'Shipping & Armored Transit Policy'),
        ('returns', 'Return & Exchange Policy'),
        ('faq', 'Frequently Asked Questions'),
        ('contact', 'Contact & Salon Location'),
        ('custom', 'Custom Editorial Page'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    page_type = models.CharField(max_length=30, choices=PAGE_TYPES, default='custom')
    eyebrow = models.CharField(max_length=150, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    body_html = models.TextField(help_text='Rich HTML content formatted for luxury display')
    blocks_json = models.JSONField(default=list, blank=True, help_text='Structured content blocks')
    meta_title = models.CharField(max_length=150, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    social_share_image = models.ImageField(upload_to='pages/seo/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Page Content'
        verbose_name_plural = 'Page Contents'

    def __str__(self):
        return f"{self.title} (/{self.slug}/)"


# ==============================================================================
# 6. EMAIL & MESSAGING NOTIFICATION TEMPLATES
# ==============================================================================
class EmailTemplate(models.Model):
    TEMPLATE_KEYS = [
        ('order_confirmation', 'Order Confirmation Email'),
        ('order_shipped', 'Order Dispatched / In Transit Email'),
        ('order_delivered', 'Order Delivered Email'),
        ('refund_processed', 'Refund Processed Email'),
        ('welcome_customer', 'Welcome New Customer Email'),
        ('whatsapp_confirmation', 'WhatsApp Order Confirmation Message'),
        ('whatsapp_shipped', 'WhatsApp Dispatch Update Message'),
    ]

    template_key = models.CharField(max_length=50, choices=TEMPLATE_KEYS, unique=True)
    name = models.CharField(max_length=150)
    subject = models.CharField(max_length=255, help_text='Email subject line (supports {customer_name}, {order_number})')
    body_text = models.TextField(help_text='Message body with variables: {customer_name}, {order_number}, {total_amount}, {tracking_link}, {arrival_date}')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Email / WhatsApp Template'
        verbose_name_plural = 'Email & WhatsApp Templates'

    def __str__(self):
        return self.name


# ==============================================================================
# 7. SHIPPING RULES & DELIVERY TIERS
# ==============================================================================
class StoreShippingRule(models.Model):
    name = models.CharField(max_length=100, default='Standard Delivery')
    code = models.CharField(max_length=30, unique=True, default='standard')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    free_above_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_time_text = models.CharField(max_length=100, default='3 to 5 business days')
    note = models.CharField(max_length=200, default='Fully insured armored courier transit')
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Shipping Rule'
        verbose_name_plural = 'Shipping Rules'

    def __str__(self):
        return f"{self.name} (₹{self.price})"


# ==============================================================================
# 8. AUDIT LOG & 30-DAY TRASH RETENTION
# ==============================================================================
class AdminAuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted / Trashed'),
        ('restore', 'Restored'),
        ('publish', 'Published'),
        ('login', 'User Login'),
        ('refund', 'Issued Refund'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_email = models.EmailField(blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=255)
    changes_summary = models.TextField(blank=True)
    old_data_json = models.JSONField(default=dict, blank=True)
    new_data_json = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.user_email} - {self.get_action_display()} {self.model_name}: {self.object_repr}"


class TrashItem(models.Model):
    """Safely stores deleted items for 30 days before permanent purging."""
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255)
    serialized_data = models.JSONField()
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-deleted_at']
        verbose_name = 'Trash Item'
        verbose_name_plural = 'Trash Items'

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trashed: {self.model_name} #{self.object_id} ({self.object_repr})"

    @property
    def days_remaining(self):
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)
