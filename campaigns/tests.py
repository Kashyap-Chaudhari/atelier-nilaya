from django.test import TestCase, Client
from django.urls import reverse
from campaigns.models import JewelleryCampaign, JewelleryCategory, JewelleryProduct

class JewelleryCampaignTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.campaign1 = JewelleryCampaign.objects.create(
            title="THE ROYAL BRIDAL EDIT",
            slug="royal-bridal-edit-test",
            eyebrow="HAUTE JOAILLERIE",
            headline_sub="An Imperial Odyssey",
            description="Indian bridal gold jewellery crafted for eternity.",
            display_order=1,
            is_active=True,
            theme_accent="gold",
            composition_style="sculptural-bevel"
        )
        self.campaign2 = JewelleryCampaign.objects.create(
            title="THE DIAMOND ATELIER",
            slug="diamond-atelier-test",
            eyebrow="SOLITAIRE CREATION",
            headline_sub="Refracting Pure Light",
            description="Luxury diamond necklaces with breathtaking movement.",
            display_order=2,
            is_active=True,
            theme_accent="champagne",
            composition_style="angled-facet"
        )

        # Categories & Products
        self.cat_neck = JewelleryCategory.objects.create(
            name="Necklaces",
            slug="necklaces",
            subtitle="ROYAL CHOKERS, RANI HAAR & KANTHA MALAS",
            description="Handcrafted necklaces in 22K & 24K gold.",
            display_order=1,
            is_active=True
        )
        self.prod_neck1 = JewelleryProduct.objects.create(
            category=self.cat_neck,
            name="Imperial Navratna Choker Suite",
            eyebrow="24K ROYAL KUNDAN",
            price=385000.00,
            metal_purity="24K Imperial Gold",
            gemstone_details="Uncut Polki & 9 Imperial Gemstones",
            short_description="A ceremonial royal choker handcrafted with nine sacred gemstones.",
            is_featured=True,
            is_in_stock=True,
            display_order=1
        )
        self.prod_neck2 = JewelleryProduct.objects.create(
            category=self.cat_neck,
            name="Basra Pearl Rani Haar",
            eyebrow="HERITAGE DYNASTY ARCHIVE",
            price=540000.00,
            metal_purity="22K Hallmark Gold",
            gemstone_details="Natural Basra Pearls",
            short_description="Magnificent seven-row pearl necklace.",
            is_featured=False,
            is_in_stock=True,
            display_order=2
        )

    def test_campaign_model_properties(self):
        self.assertEqual(self.campaign1.formatted_order, "01")
        self.assertEqual(self.campaign2.formatted_order, "02")
        self.assertEqual(str(self.campaign1), "01 — THE ROYAL BRIDAL EDIT")

    def test_category_and_product_models(self):
        self.assertEqual(self.cat_neck.products.count(), 2)
        self.assertEqual(self.prod_neck1.formatted_price, "₹3,85,000")
        self.assertEqual(self.prod_neck2.formatted_price, "₹5,40,000")
        self.assertTrue(self.prod_neck1.sku.startswith("AAR-NEC-"))

    def test_hero_view(self):
        response = self.client.get(reverse('campaigns:hero'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "THE UNVEILING ATELIER")
        self.assertContains(response, "THE ROYAL BRIDAL EDIT")
        self.assertIn('campaigns', response.context)
        self.assertIn('campaigns_json', response.context)
        self.assertEqual(response.context['total_campaigns'], 2)
        self.assertIn('categories', response.context)

    def test_aaranya_navigation_and_mega_menu(self):
        """Verify Aaranya navigation bar and mega menu are rendered without altering hero"""
        response = self.client.get(reverse('campaigns:hero'))
        self.assertEqual(response.status_code, 200)
        # Brand identity
        self.assertContains(response, "AARANYA")
        self.assertContains(response, "THE ART OF BECOMING HEIRLOOM")
        # Navigation bar
        self.assertContains(response, "aaranya-category-navbar")
        self.assertContains(response, "New &amp; Featured")
        self.assertContains(response, "Necklaces")
        self.assertContains(response, "Earrings")
        self.assertContains(response, "Rings")
        self.assertContains(response, "Bangles")
        self.assertContains(response, "Bridal Jewellery")
        self.assertContains(response, "Temple Jewellery")
        self.assertContains(response, "Diamond Jewellery")
        self.assertContains(response, "Men's Jewellery")
        self.assertContains(response, "Gifts")
        # Mega menu container
        self.assertContains(response, "aaranya-mega-menu-container")
        self.assertContains(response, "aaranya-menu-panel")
        # Mobile drawer
        self.assertContains(response, "aaranya-mobile-drawer")
        self.assertContains(response, "aaranya-mobile-menu-btn")
        # Unaltered hero components
        self.assertContains(response, "atelier-hero-section")
        self.assertContains(response, "zone-story-rail")
        self.assertContains(response, "zone-video-stage")
        self.assertContains(response, "zone-next-preview")

    def test_category_product_list_view(self):
        """Test dedicated category page view"""
        url = reverse('campaigns:category_products', kwargs={'slug': 'necklaces'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Necklaces")
        self.assertContains(response, "Imperial Navratna Choker Suite")
        self.assertContains(response, "Basra Pearl Rani Haar")
        self.assertContains(response, "₹3,85,000")
        self.assertContains(response, "₹5,40,000")
        self.assertEqual(len(response.context['products']), 2)

    def test_vault_all_products_view(self):
        """Test complete vault view"""
        url = reverse('campaigns:vault')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Jewellery Artworks")
        self.assertEqual(len(response.context['products']), 2)

    def test_detail_view(self):
        response = self.client.get(reverse('campaigns:detail', kwargs={'slug': self.campaign1.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "THE ROYAL BRIDAL EDIT")
        self.assertContains(response, "Indian bridal gold jewellery")

    def test_api_view(self):
        response = self.client.get(reverse('campaigns:api_campaigns'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['campaigns']), 2)
