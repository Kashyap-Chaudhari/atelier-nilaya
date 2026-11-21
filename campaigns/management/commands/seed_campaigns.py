import os
import urllib.request
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.conf import settings
from campaigns.models import JewelleryCampaign

CAMPAIGNS_DATA = [
    {
        'title': 'THE ROYAL BRIDAL EDIT',
        'slug': 'royal-bridal-edit',
        'eyebrow': 'HAUTE JOAILLERIE • BRIDAL OPULENCE',
        'headline_sub': 'An Imperial Odyssey In Handcrafted 24K Gold',
        'description': 'Indian bridal gold jewellery, handcrafted kundan, polki and traditional ornaments sculpted for heirloom splendour. Where generations of craftsmanship become an eternal part of your story.',
        'cta_text': 'EXPLORE ROYAL BRIDAL',
        'cta_url': '#royal-bridal',
        'display_order': 1,
        'curator_note': 'Curated for the Modern Maharani • Master Goldsmith Edition',
        'provenance_tag': '24K KUNDAN & UNCUT POLKI • JADAU GUILD CERTIFIED',
        'theme_accent': 'gold',
        'composition_style': 'sculptural-bevel',
        'video_desktop_src': 'https://assets.mixkit.co/videos/50791/50791-720.mp4',
        'video_mobile_src': 'https://assets.mixkit.co/videos/50791/50791-360.mp4',
        'poster_src': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=1600&q=85',
        'fallback_bg': (24, 20, 16),
        'fallback_accent': (173, 145, 97),
    },
    {
        'title': 'THE DIAMOND ATELIER',
        'slug': 'diamond-atelier',
        'eyebrow': 'LUMINOSITY UNVEILED • SOLITAIRE CREATION',
        'headline_sub': 'Refracting Pure Light into Eternal Scintillation',
        'description': 'Luxury diamond necklaces, close-up gemstone details and sophisticated editorial movement. Each pavilion and facet mathematically calibrated to ignite incomparable brilliance.',
        'cta_text': 'DISCOVER DIAMOND ATELIER',
        'cta_url': '#diamond-atelier',
        'display_order': 2,
        'curator_note': 'D Flawless Solitaires • Triple Excellent Ideal Cut',
        'provenance_tag': 'TYPE IIA DIAMONDS • GIA & DE BEERS VERIFIED',
        'theme_accent': 'champagne',
        'composition_style': 'angled-facet',
        'video_desktop_src': 'https://assets.mixkit.co/videos/20877/20877-720.mp4',
        'video_mobile_src': 'https://assets.mixkit.co/videos/20877/20877-360.mp4',
        'poster_src': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=1600&q=85',
        'fallback_bg': (16, 17, 20),
        'fallback_accent': (215, 193, 154),
    },
    {
        'title': 'EVERYDAY ELEGANCE',
        'slug': 'everyday-elegance',
        'eyebrow': 'CONTEMPORARY SILHOUETTES • MINIMALIST LUXE',
        'headline_sub': 'Fluid Sensuality Designed for the Modern Skin',
        'description': 'Minimal gold jewellery, delicate chains, rings, modern earrings and elegant everyday styling. Architectural simplicity meeting effortless second-skin refinement.',
        'cta_text': 'SHOP EVERYDAY LUXURY',
        'cta_url': '#everyday-elegance',
        'display_order': 3,
        'curator_note': '18K Recycled Solid Gold • Ergonomic Micro-Pavé',
        'provenance_tag': 'RESPONSIBLE JEWELLERY COUNCIL (RJC) ACCREDITED',
        'theme_accent': 'charcoal',
        'composition_style': 'editorial-monolith',
        'video_desktop_src': 'https://assets.mixkit.co/videos/34611/34611-720.mp4',
        'video_mobile_src': 'https://assets.mixkit.co/videos/34611/34611-360.mp4',
        'poster_src': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=1600&q=85',
        'fallback_bg': (23, 22, 19),
        'fallback_accent': (200, 180, 140),
    },
    {
        'title': 'THE HERITAGE COLLECTION',
        'slug': 'heritage-collection',
        'eyebrow': 'ARCHIVAL MASTERWORKS • TIMELESS PROVENANCE',
        'headline_sub': 'A Sacred Dialogue Between Millennia of Craft',
        'description': 'Antique gold, traditional craftsmanship, intricate Indian designs and heritage-inspired jewellery. Revered Nakashi repoussé and filigree revived from royal palace treasuries.',
        'cta_text': 'UNVEIL HERITAGE ARCHIVE',
        'cta_url': '#heritage-collection',
        'display_order': 4,
        'curator_note': 'Temple Goldsmith Guild • Antique 22K Patina',
        'provenance_tag': 'HISTORIC NAKASHI REPOUSSÉ • MUSEUM PROVENANCE',
        'theme_accent': 'burgundy',
        'composition_style': 'geometric-arch',
        'video_desktop_src': 'https://assets.mixkit.co/videos/2865/2865-720.mp4',
        'video_mobile_src': 'https://assets.mixkit.co/videos/2865/2865-360.mp4',
        'poster_src': 'https://images.unsplash.com/photo-1603561591411-07134e71a2a9?auto=format&fit=crop&w=1600&q=85',
        'fallback_bg': (35, 18, 22),
        'fallback_accent': (173, 145, 97),
    },
]

class Command(BaseCommand):
    help = 'Seeds database with four distinctive luxury jewellery campaigns and downloads media assets.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("✦ Beginning The Unveiling Atelier Campaign Seeding ✦"))

        # 1. Create Superuser if absent
        if not User.objects.filter(username='atelier_admin').exists():
            User.objects.create_superuser('atelier_admin', 'curator@unveilingatelier.luxury', 'atelier_luxury')
            self.stdout.write(self.style.SUCCESS("Created admin user: atelier_admin / atelier_luxury"))

        # Base directories
        video_desk_dir = Path(settings.MEDIA_ROOT) / 'campaigns' / 'videos' / 'desktop'
        video_mob_dir = Path(settings.MEDIA_ROOT) / 'campaigns' / 'videos' / 'mobile'
        poster_desk_dir = Path(settings.MEDIA_ROOT) / 'campaigns' / 'posters' / 'desktop'
        poster_mob_dir = Path(settings.MEDIA_ROOT) / 'campaigns' / 'posters' / 'mobile'

        for d in [video_desk_dir, video_mob_dir, poster_desk_dir, poster_mob_dir]:
            d.mkdir(parents=True, exist_ok=True)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

        for item in CAMPAIGNS_DATA:
            slug = item['slug']
            self.stdout.write(f"\nProcessing Campaign {item['display_order']:02d}: {item['title']}...")

            # --- Video Desktop ---
            v_desk_name = f"{slug}-desktop.mp4"
            v_desk_path = video_desk_dir / v_desk_name
            if not v_desk_path.exists() or v_desk_path.stat().st_size < 1000:
                self.stdout.write(f"  Downloading desktop video for {slug}...")
                try:
                    req = urllib.request.Request(item['video_desktop_src'], headers=headers)
                    with urllib.request.urlopen(req, timeout=30) as resp, open(v_desk_path, 'wb') as f:
                        f.write(resp.read())
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Saved desktop video ({v_desk_path.stat().st_size / 1048576:.2f} MB)"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Video download failed ({e}), creating fallback placeholder"))
                    with open(v_desk_path, 'wb') as f:
                        f.write(b"")

            # --- Video Mobile ---
            v_mob_name = f"{slug}-mobile.mp4"
            v_mob_path = video_mob_dir / v_mob_name
            if not v_mob_path.exists() or v_mob_path.stat().st_size < 1000:
                self.stdout.write(f"  Downloading mobile video for {slug}...")
                try:
                    req = urllib.request.Request(item['video_mobile_src'], headers=headers)
                    with urllib.request.urlopen(req, timeout=30) as resp, open(v_mob_path, 'wb') as f:
                        f.write(resp.read())
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Saved mobile video ({v_mob_path.stat().st_size / 1048576:.2f} MB)"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Mobile video download failed ({e}), copying desktop video"))
                    if v_desk_path.exists() and v_desk_path.stat().st_size > 0:
                        v_mob_path.write_bytes(v_desk_path.read_bytes())

            # --- Poster Desktop & Mobile ---
            p_desk_name = f"{slug}-poster-desktop.jpg"
            p_desk_path = poster_desk_dir / p_desk_name
            p_mob_name = f"{slug}-poster-mobile.jpg"
            p_mob_path = poster_mob_dir / p_mob_name

            if not p_desk_path.exists() or not p_mob_path.exists():
                self.stdout.write(f"  Downloading & processing poster for {slug}...")
                downloaded = False
                try:
                    req = urllib.request.Request(item['poster_src'], headers=headers)
                    with urllib.request.urlopen(req, timeout=25) as resp:
                        img_bytes = resp.read()
                        raw_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                        downloaded = True
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  Poster download failed ({e}), generating luxury canvas"))
                    raw_img = Image.new('RGB', (1600, 1067), color=item['fallback_bg'])
                    draw = ImageDraw.Draw(raw_img)
                    draw.rectangle([60, 60, 1540, 1007], outline=item['fallback_accent'], width=2)
                    draw.text((100, 500), f"ATELIER ARCHIVE — {item['title']}", fill=(244, 240, 232))

                # Crop Desktop (1600x900)
                desk_ratio = 16 / 9
                w, h = raw_img.size
                if w / h > desk_ratio:
                    new_w = int(h * desk_ratio)
                    left = (w - new_w) // 2
                    desk_img = raw_img.crop((left, 0, left + new_w, h))
                else:
                    new_h = int(w / desk_ratio)
                    top = (h - new_h) // 2
                    desk_img = raw_img.crop((0, top, w, top + new_h))
                desk_img = desk_img.resize((1600, 900), Image.Resampling.LANCZOS)
                desk_img.save(p_desk_path, 'JPEG', quality=88, optimize=True)

                # Crop Mobile (720x1280 portrait)
                mob_ratio = 9 / 16
                if w / h > mob_ratio:
                    new_w = int(h * mob_ratio)
                    left = (w - new_w) // 2
                    mob_img = raw_img.crop((left, 0, left + new_w, h))
                else:
                    new_h = int(w / mob_ratio)
                    top = (h - new_h) // 2
                    mob_img = raw_img.crop((0, top, w, top + new_h))
                mob_img = mob_img.resize((720, 1280), Image.Resampling.LANCZOS)
                mob_img.save(p_mob_path, 'JPEG', quality=88, optimize=True)

                self.stdout.write(self.style.SUCCESS(f"  ✓ Processed desktop & mobile posters for {slug}"))

            # --- Create or Update Campaign in Database ---
            campaign, created = JewelleryCampaign.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': item['title'],
                    'eyebrow': item['eyebrow'],
                    'headline_sub': item['headline_sub'],
                    'description': item['description'],
                    'cta_text': item['cta_text'],
                    'cta_url': item['cta_url'],
                    'display_order': item['display_order'],
                    'curator_note': item['curator_note'],
                    'provenance_tag': item['provenance_tag'],
                    'theme_accent': item['theme_accent'],
                    'composition_style': item['composition_style'],
                    'is_active': True,
                    'video_desktop': f"campaigns/videos/desktop/{v_desk_name}",
                    'video_mobile': f"campaigns/videos/mobile/{v_mob_name}",
                    'poster_desktop': f"campaigns/posters/desktop/{p_desk_name}",
                    'poster_mobile': f"campaigns/posters/mobile/{p_mob_name}",
                }
            )
            action_label = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"  ✓ {action_label} JewelleryCampaign record: {campaign}"))

        self.stdout.write(self.style.SUCCESS("\n✦ Successfully Seeded All 4 Luxury Jewellery Campaigns! ✦"))
