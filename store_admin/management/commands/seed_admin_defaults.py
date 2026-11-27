import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store_admin.models import (
    AdminProfile, StoreSettings, ThemeSettings, HeaderMenuItem,
    FooterColumn, FooterLink, FeaturedEditBlock, FeaturedEditTile,
    StoreShippingRule, EmailTemplate, PageContent, HomepageSection
)

class Command(BaseCommand):
    help = "Seeds initial StoreSettings, Theme, Navigation, Shipping, and Admin RBAC profiles"

    def handle(self, *args, **options):
        self.stdout.write("Seeding store_admin defaults...")

        # 1. Ensure Super Admin Profile
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            profile, created = AdminProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'role': AdminProfile.ROLE_SUPER_ADMIN,
                    'display_title': 'Master Curator & Owner',
                    'is_active_staff': True,
                }
            )
            self.stdout.write(f"✓ Super Admin profile linked: {admin_user.username}")

        # 2. Store Settings
        settings = StoreSettings.get_settings()
        settings.store_name = 'Atelier Nilaya'
        settings.brand_subname = 'Haute Joaillerie'
        settings.tagline = 'The Art of Becoming Heirloom'
        settings.provenance_city = 'Surat &bull; Est. 1954'
        settings.gst_rate_percent = 18.00
        settings.save()
        self.stdout.write("✓ StoreSettings configured")

        # 3. Theme Settings
        theme = ThemeSettings.get_theme()
        theme.primary_color = '#642D3B'
        theme.accent_gold = '#B8893B'
        theme.bg_canvas = '#FAF7F2'
        theme.surface_card = '#FFFFFF'
        theme.text_primary = '#2B1A1F'
        theme.save()
        self.stdout.write("✓ ThemeSettings configured")

        # 4. Header Menu Items
        menu_items_data = [
            ("Home", "/", 1),
            ("New & Featured", "/vault/?filter=new", 2),
            ("Necklaces", "/vault/?cat=necklaces", 3),
            ("Earrings", "/vault/?cat=earrings", 4),
            ("Rings", "/vault/?cat=rings", 5),
            ("Bangles", "/vault/?cat=bangles", 6),
            ("Bridal Jewellery", "/vault/?cat=bridal", 7),
            ("Temple Jewellery", "/vault/?cat=temple", 8),
            ("Diamond Jewellery", "/vault/?cat=diamonds", 9),
            ("Men's Jewellery", "/vault/?cat=mens", 10),
            ("Gifts", "/vault/?cat=gifts", 11),
            ("About Us", "/about/", 12),
            ("Track Your Order", "/orders/track/", 13),
        ]
        for title, url, order in menu_items_data:
            HeaderMenuItem.objects.get_or_create(
                title=title,
                defaults={'url': url, 'display_order': order, 'is_active': True}
            )
        self.stdout.write("✓ HeaderMenuItem items seeded")

        # 5. Footer Columns & Links
        col_heritage, _ = FooterColumn.objects.get_or_create(title="The Maison", defaults={'display_order': 1})
        FooterLink.objects.get_or_create(column=col_heritage, label="Our Heritage Story", defaults={'url': '/about/', 'display_order': 1})
        FooterLink.objects.get_or_create(column=col_heritage, label="Surat Karigar Benches", defaults={'url': '/about/#karigars', 'display_order': 2})
        FooterLink.objects.get_or_create(column=col_heritage, label="BIS 916 Provenance", defaults={'url': '/terms-of-provenance/', 'display_order': 3})

        col_service, _ = FooterColumn.objects.get_or_create(title="Client Concierge", defaults={'display_order': 2})
        FooterLink.objects.get_or_create(column=col_service, label="Track Your Order", defaults={'url': '/orders/track/', 'display_order': 1})
        FooterLink.objects.get_or_create(column=col_service, label="Schedule Salon Viewing", defaults={'url': '/#appointment', 'display_order': 2})
        FooterLink.objects.get_or_create(column=col_service, label="Client Folio & Wishlist", defaults={'url': '/wishlist/', 'display_order': 3})

        col_legal, _ = FooterColumn.objects.get_or_create(title="Statutory & Trust", defaults={'display_order': 3})
        FooterLink.objects.get_or_create(column=col_legal, label="Privacy Policy", defaults={'url': '/privacy-policy/', 'display_order': 1})
        FooterLink.objects.get_or_create(column=col_legal, label="Terms of Provenance", defaults={'url': '/terms-of-provenance/', 'display_order': 2})
        self.stdout.write("✓ Footer columns and links seeded")

        # 6. Shipping Rules
        StoreShippingRule.objects.get_or_create(
            code='standard',
            defaults={
                'name': 'Standard Insured Delivery',
                'price': 0.00,
                'free_above_amount': 0.00,
                'delivery_time_text': '3 to 5 business days',
                'note': 'Armored white-glove transit across India',
                'display_order': 1
            }
        )
        StoreShippingRule.objects.get_or_create(
            code='express',
            defaults={
                'name': 'Express Overnight Vault Transit',
                'price': 149.00,
                'free_above_amount': 100000.00,
                'delivery_time_text': 'Next-day priority delivery',
                'note': 'Priority armored express courier dispatch',
                'display_order': 2
            }
        )
        self.stdout.write("✓ StoreShippingRule seeded")

        # 7. Featured Edit Block
        feat_edit = FeaturedEditBlock.get_active()
        if not feat_edit:
            feat_edit = FeaturedEditBlock.objects.create(
                title='The Lapidary Benches',
                kicker='Curatorial Edit &bull; Autumn 2026',
                body='Over seven decades of uncompromised Surat stone cutting and sacred gold alloy metallurgy.',
                button_text='EXPLORE COLLECTION',
                button_link='/vault/',
                is_active=True
            )
            # Create sample tiles
            FeaturedEditTile.objects.create(
                edit_block=feat_edit,
                tile_type='product_grid',
                title='Royal Polki & Solitaire Suites',
                subtitle='Handcrafted in certified 22K yellow gold',
                copy='Curated signature bridal and cocktail pieces from our private Surat archives.',
                button_text='VIEW SUITE',
                button_link='/vault/',
                product_ids='1, 2, 3',
                display_order=1
            )
        self.stdout.write("✓ FeaturedEditBlock seeded")

        # 8. Email Templates
        EmailTemplate.objects.get_or_create(
            template_key='order_confirmation',
            defaults={
                'name': 'Order Confirmation Email',
                'subject': 'Your Atelier Nilaya Acquisition Confirmed — Ref #{order_number}',
                'body_text': (
                    "Dear {customer_name},\n\n"
                    "We are honored to confirm your private acquisition #{order_number} with Atelier Nilaya.\n\n"
                    "Total Amount: ₹{total_amount}\n"
                    "Estimated Arrival: {arrival_date}\n\n"
                    "Our master karigars in Surat have commenced final inspection and BIS hallmarking.\n"
                    "Track your milestone here: {tracking_link}\n\n"
                    "Yours in Haute Joaillerie,\nAtelier Nilaya Concierge"
                ),
                'is_active': True
            }
        )
        EmailTemplate.objects.get_or_create(
            template_key='whatsapp_confirmation',
            defaults={
                'name': 'WhatsApp Order Milestone Message',
                'subject': 'WhatsApp Order Update',
                'body_text': '✨ *Atelier Nilaya*: Your acquisition #{order_number} is confirmed! Estimated arrival: {arrival_date}. Track here: {tracking_link}',
                'is_active': True
            }
        )
        self.stdout.write("✓ Email & WhatsApp templates seeded")

        self.stdout.write(self.style.SUCCESS("All store_admin defaults seeded successfully!"))
