import os
from django.db import models
from django.utils.text import slugify
from .validators import validate_video_file, validate_image_file

class JewelleryCampaign(models.Model):
    THEME_CHOICES = [
        ('gold', 'Imperial Gold (#AD9161)'),
        ('champagne', 'Champagne Solitaire (#D7C19A)'),
        ('burgundy', 'Muted Burgundy (#512C31)'),
        ('charcoal', 'Nocturne Charcoal (#171613)'),
    ]

    COMPOSITION_CHOICES = [
        ('sculptural-bevel', 'Sculptural Bevel Cut (Diagonal Architectural Notch)'),
        ('geometric-arch', 'Curated Architectural Arch & Frame'),
        ('angled-facet', 'Faceted Diamond Contour'),
        ('editorial-monolith', 'Monolithic Asymmetric Pillar'),
    ]

    title = models.CharField(max_length=200, help_text="Primary campaign title (e.g. 'THE ROYAL BRIDAL EDIT')")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    eyebrow = models.CharField(max_length=150, help_text="Small uppercase category (e.g. 'HAUTE JOAILLERIE')")
    headline_sub = models.CharField(max_length=250, blank=True, help_text="Poetic sub-headline (e.g. 'A legacy, preserved in gold.')")
    description = models.TextField(help_text="Short emotional description of the collection")
    
    video_desktop = models.FileField(
        upload_to='campaigns/videos/desktop/',
        validators=[validate_video_file],
        help_text="Desktop 16:9/4:3 campaign video (MP4/WebM, max 35MB)"
    )
    video_mobile = models.FileField(
        upload_to='campaigns/videos/mobile/',
        validators=[validate_video_file],
        blank=True,
        null=True,
        help_text="Optional mobile 9:16 portrait video (MP4/WebM, max 25MB)"
    )
    poster_desktop = models.ImageField(
        upload_to='campaigns/posters/desktop/',
        validators=[validate_image_file],
        help_text="High-resolution desktop poster fallback image"
    )
    poster_mobile = models.ImageField(
        upload_to='campaigns/posters/mobile/',
        validators=[validate_image_file],
        blank=True,
        null=True,
        help_text="Mobile portrait poster fallback image"
    )
    
    cta_text = models.CharField(max_length=100, default='EXPLORE COLLECTION')
    cta_url = models.CharField(max_length=300, default='#')
    display_order = models.PositiveIntegerField(default=1, help_text="Sequence index for carousel presentation")
    is_active = models.BooleanField(default=True, help_text="Include in live hero presentation")
    
    # Luxury editorial metadata
    curator_note = models.CharField(max_length=255, blank=True, default="Private Exhibition • Atelier Masterpiece")
    provenance_tag = models.CharField(max_length=120, blank=True, default="24K PURE GOLD • HANDCRAFTED")
    theme_accent = models.CharField(max_length=50, choices=THEME_CHOICES, default='gold')
    composition_style = models.CharField(max_length=50, choices=COMPOSITION_CHOICES, default='sculptural-bevel')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Jewellery Campaign'
        verbose_name_plural = 'Jewellery Campaigns'

    def __str__(self):
        return f"{self.formatted_order} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def formatted_order(self):
        return f"{self.display_order:02d}"

    @property
    def video_desktop_url(self):
        if self.video_desktop and hasattr(self.video_desktop, 'url'):
            return self.video_desktop.url
        return ''

    @property
    def video_mobile_url(self):
        if self.video_mobile and hasattr(self.video_mobile, 'url'):
            return self.video_mobile.url
        return self.video_desktop_url

    @property
    def poster_desktop_url(self):
        if self.poster_desktop and hasattr(self.poster_desktop, 'url'):
            return self.poster_desktop.url
        return ''

    @property
    def poster_mobile_url(self):
        if self.poster_mobile and hasattr(self.poster_mobile, 'url'):
            return self.poster_mobile.url
        return self.poster_desktop_url


class JewelleryCategory(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text="Category name (e.g. 'Necklaces')")
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    subtitle = models.CharField(max_length=255, blank=True, help_text="Curatorial subtitle (e.g. 'ROYAL CHOKERS, RANI HAAR & KANTHA MALAS')")
    description = models.TextField(blank=True, help_text="Curatorial description of this category")
    banner_image = models.ImageField(upload_to='categories/banners/', blank=True, null=True)
    banner_url_fallback = models.CharField(max_length=500, blank=True)
    display_order = models.PositiveIntegerField(default=1)
    base_metal = models.CharField(max_length=50, default='yellow_gold', choices=[
        ('yellow_gold', 'Yellow Gold'),
        ('rose_gold', 'Rose Gold'),
        ('platinum', 'Platinum'),
        ('silver', 'Silver')
    ])
    gold_weight_grams = models.DecimalField(max_digits=8, decimal_places=3, default=12.500, help_text="Gross precious metal weight in grams")
    making_charge_type = models.CharField(max_length=20, default='per_gram', choices=[
        ('per_gram', 'Per Gram (₹)'),
        ('flat', 'Flat Fee (₹)'),
        ('percentage', 'Percentage (%)')
    ])
    making_charge_value = models.DecimalField(max_digits=10, decimal_places=2, default=850.00, help_text="Bench karigar fee")
    stone_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Precious stone value in INR")
    is_one_of_a_kind = models.BooleanField(default=False, help_text="Only 1 available in vault")
    is_made_to_order = models.BooleanField(default=False, help_text="Crafted on order at bench")
    making_days = models.PositiveIntegerField(default=14, help_text="Bench craftsmanship duration in days")
    advance_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=25.00, help_text="Minimum advance required for made-to-order")
    stock_quantity = models.PositiveIntegerField(default=5, help_text="Current available stock")
    huid_number = models.CharField(max_length=50, blank=True, default='', help_text="Unique BIS HUID identifier")
    available_sizes = models.CharField(max_length=255, default='Standard,10,12,14,16,18,20', help_text="Comma-separated sizes (e.g. Ring sizes or Bangle diameters)")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Jewellery Category'
        verbose_name_plural = 'Jewellery Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def product_count(self):
        return self.products.filter(is_in_stock=True).count()

    @property
    def display_banner(self):
        if self.banner_image and hasattr(self.banner_image, 'url'):
            return self.banner_image.url
        return self.banner_url_fallback


class JewelleryProduct(models.Model):
    category = models.ForeignKey(JewelleryCategory, on_delete=models.CASCADE, related_name='products')
    subcategory = models.CharField(max_length=120, blank=True, default='', db_index=True, help_text="Subcategory (e.g. 'Antique Bangles', 'Choker Sets')")
    tags = models.TextField(blank=True, default='', help_text="Semicolon-separated tags, occasions, and menu collections")
    name = models.CharField(max_length=200, help_text="Product title")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    eyebrow = models.CharField(max_length=150, blank=True, help_text="Hallmark or purity tag (e.g. '24K ROYAL KUNDAN')")
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in INR (₹)")
    metal_purity = models.CharField(max_length=120, default='22K Imperial Gold')
    gemstone_details = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url_fallback = models.CharField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_in_stock = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=1)
    base_metal = models.CharField(max_length=50, default='yellow_gold', choices=[
        ('yellow_gold', 'Yellow Gold'),
        ('rose_gold', 'Rose Gold'),
        ('platinum', 'Platinum'),
        ('silver', 'Silver')
    ])
    gold_weight_grams = models.DecimalField(max_digits=8, decimal_places=3, default=12.500, help_text="Gross precious metal weight in grams")
    making_charge_type = models.CharField(max_length=20, default='per_gram', choices=[
        ('per_gram', 'Per Gram (₹)'),
        ('flat', 'Flat Fee (₹)'),
        ('percentage', 'Percentage (%)')
    ])
    making_charge_value = models.DecimalField(max_digits=10, decimal_places=2, default=850.00, help_text="Bench karigar fee")
    stone_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Precious stone value in INR")
    is_one_of_a_kind = models.BooleanField(default=False, help_text="Only 1 available in vault")
    is_made_to_order = models.BooleanField(default=False, help_text="Crafted on order at bench")
    making_days = models.PositiveIntegerField(default=14, help_text="Bench craftsmanship duration in days")
    advance_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=25.00, help_text="Minimum advance required for made-to-order")
    stock_quantity = models.PositiveIntegerField(default=5, help_text="Current available stock")
    huid_number = models.CharField(max_length=50, blank=True, default='', help_text="Unique BIS HUID identifier")
    available_sizes = models.CharField(max_length=255, default='Standard,10,12,14,16,18,20', help_text="Comma-separated sizes (e.g. Ring sizes or Bangle diameters)")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-id']
        verbose_name = 'Jewellery Product'
        verbose_name_plural = 'Jewellery Products'

    def __str__(self):
        return f"{self.name} — {self.formatted_price}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            import uuid
            cat_prefix = slugify(self.category.name)[:3].upper() if self.category else 'AAR'
            self.sku = f"AAR-{cat_prefix}-{str(uuid.uuid4())[:6].upper()}"
        super().save(*args, **kwargs)

    @property
    def formatted_price(self):
        try:
            val = int(self.price)
            s = str(val)
            if len(s) <= 3:
                res = s
            else:
                last_three = s[-3:]
                remaining = s[:-3]
                groups = []
                while remaining:
                    groups.append(remaining[-2:])
                    remaining = remaining[:-2]
                groups.reverse()
                res = ','.join(groups) + ',' + last_three
            return f"₹{res}"
        except:
            return f"₹{self.price}"

    @property
    def display_image(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return self.image_url_fallback


class GoldRate(models.Model):
    rate_24k = models.DecimalField(max_digits=10, decimal_places=2, default=7450.00, help_text="24K pure gold per gram (₹)")
    rate_22k = models.DecimalField(max_digits=10, decimal_places=2, default=6830.00, help_text="22K standard gold per gram (₹)")
    rate_18k = models.DecimalField(max_digits=10, decimal_places=2, default=5590.00, help_text="18K fine gold per gram (₹)")
    rate_platinum = models.DecimalField(max_digits=10, decimal_places=2, default=3250.00, help_text="Platinum per gram (₹)")
    rate_silver = models.DecimalField(max_digits=10, decimal_places=2, default=92.00, help_text="Silver per gram (₹)")
    effective_date = models.DateField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, default='Head Master Goldsmith')
    notes = models.CharField(max_length=255, blank=True, default='Daily benchmark bullion board rate')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Daily Gold & Precious Metal Rate'
        verbose_name_plural = 'Daily Gold & Precious Metal Rates'

    def __str__(self):
        return f"Bullion Rate {self.effective_date} (24K: ₹{self.rate_24k}/g, 22K: ₹{self.rate_22k}/g)"

    @classmethod
    def get_current_rates(cls):
        latest = cls.objects.first()
        if not latest:
            try:
                import sqlite3, os
                db_path = os.path.join(os.path.dirname(__file__), '..', 'nilaya.db')
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
                    row = conn.execute("SELECT * FROM gold_rates ORDER BY id DESC LIMIT 1").fetchone()
                    conn.close()
                    if row:
                        latest = cls.objects.create(
                            rate_24k=row['rate_24k'] or 7450,
                            rate_22k=row['rate_22k'] or 6830,
                            rate_18k=row['rate_18k'] or 5590,
                            rate_platinum=row['rate_platinum'] or 3250,
                            rate_silver=row['rate_silver'] or 92
                        )
            except Exception:
                pass
            if not latest:
                latest = cls.objects.create()
        return latest


import hashlib
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile_number = models.CharField(max_length=20, blank=True, default='', db_index=True)
    is_email_verified = models.BooleanField(default=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    resend_verification_count = models.PositiveIntegerField(default=0)
    last_resend_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.user.email}) - {'Verified' if self.is_email_verified else 'Unverified'}"

    def is_locked(self) -> bool:
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False

    def get_lock_minutes_remaining(self) -> int:
        if not self.is_locked():
            return 0
        return int((self.locked_until - timezone.now()).total_seconds() // 60) + 1

    def register_failed_attempt(self):
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=15)
        self.save(update_fields=['failed_login_attempts', 'locked_until', 'updated_at'])

    def reset_failed_attempts(self):
        if self.failed_login_attempts > 0 or self.locked_until is not None:
            self.failed_login_attempts = 0
            self.locked_until = None
            self.save(update_fields=['failed_login_attempts', 'locked_until', 'updated_at'])


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    profile, p_created = UserProfile.objects.get_or_create(user=instance)
    if p_created:
        if instance.is_superuser or instance.is_staff:
            profile.is_email_verified = True
            profile.save(update_fields=['is_email_verified'])


class AuthRateLimitLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login Attempt'),
        ('signup', 'Sign Up Attempt'),
        ('forgot_password', 'Forgot Password'),
        ('resend_verification', 'Resend Verification Email'),
    ]
    ip_address = models.GenericIPAddressField(db_index=True)
    action = models.CharField(max_length=40, choices=ACTION_CHOICES, db_index=True)
    identifier = models.CharField(max_length=150, blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    @classmethod
    def is_rate_limited(cls, ip: str, action: str, max_requests: int, window_seconds: int) -> bool:
        cutoff = timezone.now() - timezone.timedelta(seconds=window_seconds)
        cnt = cls.objects.filter(ip_address=ip, action=action, timestamp__gte=cutoff).count()
        return cnt >= max_requests

    @classmethod
    def record(cls, ip: str, action: str, identifier: str = ''):
        cls.objects.create(ip_address=ip, action=action, identifier=identifier[:150])


class CustomerPhoneOTP(models.Model):
    phone = models.CharField(max_length=15, db_index=True)
    otp_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    resend_count = models.PositiveIntegerField(default=0)
    last_sent_at = models.DateTimeField(auto_now=True)
    wrong_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Customer Phone OTP'
        verbose_name_plural = 'Customer Phone OTPs'

    @classmethod
    def hash_code(cls, code: str) -> str:
        salt = getattr(settings, 'SECRET_KEY', 'nilaya_secret_salt')[:16]
        return hashlib.sha256((str(code).strip() + salt).encode('utf-8')).hexdigest()

    def is_locked(self) -> bool:
        if self.locked_until and timezone.now() < self.locked_until:
            return True
        return False

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def verify_code(self, code: str) -> tuple[bool, str]:
        now = timezone.now()
        if self.is_locked():
            mins = int((self.locked_until - now).total_seconds() // 60) + 1
            return False, f"Too many incorrect attempts. Verification locked for {mins} minutes."
        
        if self.is_expired():
            return False, "OTP has expired. Please request a new code."

        input_hash = self.hash_code(code)
        if input_hash == self.otp_hash:
            self.wrong_attempts = 0
            self.save(update_fields=['wrong_attempts'])
            return True, "Verification successful."

        self.wrong_attempts += 1
        remaining = max(0, 5 - self.wrong_attempts)
        if self.wrong_attempts >= 5:
            self.locked_until = now + timezone.timedelta(minutes=15)
            self.save(update_fields=['wrong_attempts', 'locked_until'])
            return False, "Too many incorrect attempts. Verification locked for 15 minutes."
        else:
            self.save(update_fields=['wrong_attempts'])
            tries_text = "try" if remaining == 1 else "tries"
            return False, f"Wrong code, {remaining} {tries_text} left."

