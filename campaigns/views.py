from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView
from django.http import JsonResponse
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from .models import JewelleryCampaign, JewelleryCategory, JewelleryProduct

def enrich_product_for_gallery(prod):
    cat_slug = prod.category.slug if prod.category else 'rings'
    if 'ring' in cat_slug:
        prod.model_type = 'ring'
        prod.lifestyle_photo = '/static/lifestyle/lifestyle-product-1.webp'
        prod.lifestyle_body_part = 'hand'
    elif 'ear' in cat_slug:
        prod.model_type = 'earrings'
        prod.lifestyle_photo = '/static/lifestyle/lifestyle-product-7.webp'
        prod.lifestyle_body_part = 'ear'
    elif 'neck' in cat_slug or 'choker' in cat_slug:
        prod.model_type = 'necklace'
        prod.lifestyle_photo = '/static/lifestyle/lifestyle-product-11.webp'
        prod.lifestyle_body_part = 'neck'
    else:
        prod.model_type = 'bangle'
        prod.lifestyle_photo = '/static/lifestyle/lifestyle-product-14.webp'
        prod.lifestyle_body_part = 'wrist'

    purity = str(prod.metal_purity).lower()
    if 'platinum' in purity:
        prod.base_metal = 'platinum'
    elif 'rose' in purity:
        prod.base_metal = 'rose_gold'
    elif 'silver' in purity:
        prod.base_metal = 'silver'
    else:
        prod.base_metal = 'yellow_gold'

    gem = str(prod.gemstone_details).lower()
    if 'emerald' in gem:
        prod.stone_color = '#185E48'
    elif 'sapphire' in gem:
        prod.stone_color = '#D94E76'
    elif 'ruby' in gem or 'spinel' in gem:
        prod.stone_color = '#9E1B32'
    elif 'pearl' in gem:
        prod.stone_color = '#F5F0EA'
    elif 'navratna' in gem:
        prod.stone_color = '#185E48'
    else:
        prod.stone_color = '#FFFFFF'

    from django.conf import settings
    import os
    prod_dir = os.path.join(settings.BASE_DIR, 'static', 'products', prod.slug)
    spin_dir = os.path.join(prod_dir, prod.base_metal, 'spin')
    if os.path.isdir(spin_dir) and len(os.listdir(spin_dir)) >= 12:
        prod.has_spin = True
        prod.spin_frames = len(os.listdir(spin_dir))
    else:
        prod.has_spin = False
        prod.spin_frames = 0

    base_price = float(prod.price)

    # Metal Swatches: Show a swatch only if that version really exists with its own photos
    metal_defs = {
        'yellow_gold': {'label': 'Gold', 'color': '#E6C687', 'mult': 1.0},
        'rose_gold': {'label': 'Rose Gold', 'color': '#E2A794', 'mult': 1.02},
        'platinum': {'label': 'Platinum', 'color': '#E5E8EC', 'mult': 1.08},
        'silver': {'label': 'Silver', 'color': '#D8DCE0', 'mult': 0.6},
    }
    
    prod.metals = {}
    available_metals = []
    
    if os.path.isdir(prod_dir):
        for m_key, m_info in metal_defs.items():
            m_folder = os.path.join(prod_dir, m_key)
            if os.path.isdir(m_folder):
                has_files = (
                    os.path.isfile(os.path.join(m_folder, 'front.jpg')) or
                    os.path.isfile(os.path.join(m_folder, 'front.webp')) or
                    (os.path.isdir(os.path.join(m_folder, 'spin')) and len(os.listdir(os.path.join(m_folder, 'spin'))) >= 12)
                )
                if has_files:
                    m_price = round(base_price * m_info['mult'])
                    prod.metals[m_key] = {
                        'price': m_price,
                        'in_stock': True,
                        'label': m_info['label'],
                        'color': m_info['color'],
                        'has_photos': True
                    }
                    available_metals.append({'key': m_key, **prod.metals[m_key]})
                    
    if not available_metals:
        # Default single metal piece
        b_metal = prod.base_metal if prod.base_metal in metal_defs else 'yellow_gold'
        b_info = metal_defs[b_metal]
        prod.metals[b_metal] = {
            'price': base_price,
            'in_stock': True,
            'label': b_info['label'],
            'color': b_info['color'],
            'has_photos': True
        }
        available_metals.append({'key': b_metal, **prod.metals[b_metal]})

    prod.available_metals = available_metals
    prod.metals_json = json.dumps(prod.metals)

    # Top-left tag: At most one tag; Bestseller only if real sales data says so
    if prod.is_bestseller:
        prod.tag = 'BESTSELLER'
    elif prod.is_made_to_order:
        prod.tag = 'MADE TO ORDER'
    elif prod.is_one_of_a_kind:
        prod.tag = 'ONLY 1 AVAILABLE'
    elif prod.is_featured:
        prod.tag = 'NEW'
    else:
        prod.tag = None

    if prod.id % 2 == 0:
        prod.old_price = round(base_price * 1.11)
        prod.save_percent = 10
    else:
        prod.old_price = None
        prod.save_percent = None

    return prod

@method_decorator(never_cache, name='dispatch')
class HeroAtelierView(TemplateView):
    template_name = 'campaigns/hero.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaigns = list(JewelleryCampaign.objects.filter(is_active=True).order_by('display_order', 'id'))
        context['campaigns'] = campaigns
        context['total_campaigns'] = len(campaigns)
        context['categories'] = JewelleryCategory.objects.filter(is_active=True).order_by('display_order')
        
        campaigns_data = []
        for c in campaigns:
            campaigns_data.append({
                'id': c.id,
                'order': c.formatted_order,
                'title': c.title,
                'slug': c.slug,
                'eyebrow': c.eyebrow,
                'headline_sub': c.headline_sub,
                'description': c.description,
                'video_desktop': c.video_desktop_url,
                'video_mobile': c.video_mobile_url,
                'poster_desktop': c.poster_desktop_url,
                'poster_mobile': c.poster_mobile_url,
                'cta_text': c.cta_text,
                'cta_url': c.cta_url,
                'curator_note': c.curator_note,
                'provenance_tag': c.provenance_tag,
                'theme_accent': c.theme_accent,
                'composition_style': c.composition_style,
            })
        context['campaigns_json'] = json.dumps(campaigns_data)
        
        # Load Featured Edit Section
        try:
            import sqlite3
            import os
            db_path = os.path.join(os.path.dirname(__file__), '..', 'nilaya.db')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                f_sec = conn.execute("SELECT * FROM feature_section WHERE active = 1 ORDER BY id ASC LIMIT 1").fetchone()
                if f_sec:
                    featured_edit = dict(f_sec)
                    f_tiles = conn.execute("SELECT * FROM feature_tiles WHERE feature_section_id = ? AND active = 1 ORDER BY sort_order ASC", (f_sec['id'],)).fetchall()
                    tiles_list = []
                    for t in f_tiles:
                        t_dict = dict(t)
                        if (t_dict.get('kind') == 'product_group' or t_dict.get('tile_type') == 'product_grid') and t_dict.get('product_ids'):
                            p_ids = [int(x.strip()) for x in t_dict['product_ids'].split(',') if x.strip().isdigit()]
                            if p_ids:
                                placeholders = ','.join(['?'] * len(p_ids))
                                prods_raw = conn.execute(f"SELECT * FROM products WHERE id IN ({placeholders})", p_ids).fetchall()
                                prod_map = {p['id']: dict(p) for p in prods_raw}
                                ordered_prods = []
                                for pid in p_ids:
                                    if pid in prod_map:
                                        p_info = prod_map[pid]
                                        m = p_info.get('metal', 'platinum').lower().replace(' ', '_').replace('18k_', '').replace('24k_', '')
                                        if m not in ['platinum', 'rose_gold', 'yellow_gold', 'white_gold']:
                                            m = 'platinum'
                                        p_info['resolved_image'] = f"/static/products/{p_info['slug']}/{m}/front.webp"
                                        ordered_prods.append(p_info)
                                t_dict['products'] = ordered_prods
                        tiles_list.append(t_dict)
                    featured_edit['tiles'] = tiles_list
                    context['featured_edit'] = featured_edit
                conn.close()
        except Exception as e:
            pass

        return context

class CampaignDetailView(DetailView):
    model = JewelleryCampaign
    template_name = 'campaigns/detail.html'
    context_object_name = 'campaign'

def campaigns_api(request):
    campaigns = JewelleryCampaign.objects.filter(is_active=True).order_by('display_order', 'id')
    data = [{
        'id': c.id,
        'order': c.formatted_order,
        'title': c.title,
        'eyebrow': c.eyebrow,
        'description': c.description,
        'video_desktop': c.video_desktop_url,
        'poster_desktop': c.poster_desktop_url,
    } for c in campaigns]
    return JsonResponse({'status': 'success', 'campaigns': data})

class CategoryProductListView(DetailView):
    model = JewelleryCategory
    template_name = 'campaigns/category_products.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        queryset = category.products.filter(is_in_stock=True)

        # Query Filters
        metal = self.request.GET.get('metal', 'all').strip().lower()
        if metal and metal != 'all':
            if metal == 'yellow_gold' or metal == 'gold':
                queryset = queryset.filter(metal_purity__icontains='Gold')
            elif metal == 'platinum':
                queryset = queryset.filter(metal_purity__icontains='Platinum')
            elif metal == 'rose_gold':
                queryset = queryset.filter(metal_purity__icontains='Rose')
            elif metal == 'silver':
                queryset = queryset.filter(metal_purity__icontains='Silver')

        price = self.request.GET.get('price', 'all').strip().lower()
        if price == 'under_100k':
            queryset = queryset.filter(price__lt=100000)
        elif price == '100k_250k':
            queryset = queryset.filter(price__gte=100000, price__lte=250000)
        elif price == '250k_500k':
            queryset = queryset.filter(price__gt=250000, price__lte=500000)
        elif price == 'above_500k':
            queryset = queryset.filter(price__gt=500000)

        stone = self.request.GET.get('stone', 'all').strip().lower()
        if stone and stone != 'all':
            queryset = queryset.filter(Q(gemstone_details__icontains=stone) | Q(name__icontains=stone))

        occasion = self.request.GET.get('occasion', 'all').strip().lower()
        if occasion and occasion != 'all':
            queryset = queryset.filter(Q(description__icontains=occasion) | Q(eyebrow__icontains=occasion) | Q(name__icontains=occasion))

        sort = self.request.GET.get('sort', 'featured').strip().lower()
        if sort == 'price_asc' or sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc' or sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at', '-id')
        else:
            queryset = queryset.order_by('display_order', '-is_featured', '-id')

        raw_products = list(queryset)
        enriched_products = [enrich_product_for_gallery(p) for p in raw_products]

        active_filters = []
        if metal != 'all':
            active_filters.append({'key': 'metal', 'label': f"Metal: {metal.replace('_', ' ').title()}"})
        if price != 'all':
            price_map = {
                'under_100k': 'Under ₹1,00,000',
                '100k_250k': '₹1,00,000 – ₹2,50,000',
                '250k_500k': '₹2,50,000 – ₹5,00,000',
                'above_500k': 'Above ₹5,00,000'
            }
            active_filters.append({'key': 'price', 'label': f"Price: {price_map.get(price, price)}"})
        if stone != 'all':
            active_filters.append({'key': 'stone', 'label': f"Stone: {stone.title()}"})
        if occasion != 'all':
            active_filters.append({'key': 'occasion', 'label': f"Occasion: {occasion.title()}"})

        context['products'] = enriched_products
        context['total_products'] = len(enriched_products)
        context['all_categories'] = JewelleryCategory.objects.filter(is_active=True).order_by('display_order')
        context['metal_filter'] = metal
        context['price_filter'] = price
        context['stone_filter'] = stone
        context['occasion_filter'] = occasion
        context['sort_order'] = sort
        context['active_filters'] = active_filters
        return context

class AllProductsVaultView(TemplateView):
    template_name = 'campaigns/category_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = JewelleryProduct.objects.filter(is_in_stock=True)

        cat_slug = self.request.GET.get('cat')
        active_cat = None
        if cat_slug:
            active_cat = JewelleryCategory.objects.filter(slug=cat_slug).first()
            if active_cat:
                queryset = queryset.filter(category=active_cat)

        sort = self.request.GET.get('sort', 'featured')
        if sort == 'price_low' or sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_high' or sort == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('display_order', '-is_featured', '-id')

        raw_products = list(queryset)
        enriched_products = [enrich_product_for_gallery(p) for p in raw_products]

        context['category'] = active_cat or type('DummyCat', (), {'name': 'All Jewellery Artworks', 'slug': 'vault', 'sentence': 'Explore our complete archive of handcrafted Indian royal jewellery.'})()
        context['is_vault_all'] = (active_cat is None)
        context['products'] = enriched_products
        context['total_products'] = len(enriched_products)
        context['all_categories'] = JewelleryCategory.objects.filter(is_active=True).order_by('display_order')
        context['sort_order'] = sort
        context['metal_filter'] = 'all'
        context['price_filter'] = 'all'
        context['stone_filter'] = 'all'
        context['occasion_filter'] = 'all'
        context['active_filters'] = []
        return context

class ProductDetailView(DetailView):
    model = JewelleryProduct
    template_name = 'campaigns/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        slug = self.kwargs.get('slug')
        if pk:
            return get_object_or_404(queryset, pk=pk)
        if slug:
            if slug.isdigit():
                return get_object_or_404(queryset, pk=int(slug))
            # Try exact slug match
            prod = queryset.filter(slug=slug).first()
            if prod:
                return prod
            # Try normalized slug (handle 2-2ct vs 22ct)
            slug_alt = slug.replace('-2-2ct', '-22ct') if '-2-2ct' in slug else slug.replace('-22ct', '-2-2ct')
            prod = queryset.filter(slug=slug_alt).first()
            if prod:
                return prod
            # Fallback to name or startswith
            prod = queryset.filter(slug__istartswith=slug[:15]).first()
            if prod:
                return prod
            return get_object_or_404(queryset, slug=slug)
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prod = enrich_product_for_gallery(self.object)
        context['product'] = prod
        context['metals'] = prod.metals
        context['selected_metal'] = self.request.GET.get('metal', prod.base_metal)
        context['current_price'] = prod.metals.get(context['selected_metal'], {}).get('price', prod.price)
        context['all_categories'] = JewelleryCategory.objects.filter(is_active=True).order_by('display_order')
        return context

class WishlistView(TemplateView):
    template_name = 'campaigns/wishlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ids_str = self.request.GET.get('ids', '')
        ids = [int(x) for x in ids_str.split(',') if x.isdigit()]
        if ids:
            queryset = JewelleryProduct.objects.filter(id__in=ids)
        else:
            queryset = JewelleryProduct.objects.filter(is_featured=True)[:4]
        context['products'] = [enrich_product_for_gallery(p) for p in queryset]
        context['all_categories'] = JewelleryCategory.objects.filter(is_active=True).order_by('display_order')
        return context

@csrf_exempt
def api_cart_django(request):
    from cart.views import api_get_cart, api_add_to_cart
    if request.method == 'GET':
        return api_get_cart(request)
    return api_add_to_cart(request)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def get_safe_redirect(request, default='/orders/history/'):
    from django.utils.http import url_has_allowed_host_and_scheme
    next_url = request.GET.get('next') or request.POST.get('next')
    if not next_url and request.content_type == 'application/json':
        try:
            body_data = json.loads(request.body.decode('utf-8'))
            next_url = body_data.get('next')
        except Exception:
            pass
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        if next_url in ['/checkout', '/checkout/']:
            return '/orders/checkout/'
        return next_url
    return default

@csrf_exempt
def api_wishlist_toggle_django(request):
    prod_id = request.GET.get('product_id') or request.POST.get('product_id') or ''
    if not request.user.is_authenticated:
        referer = request.META.get('HTTP_REFERER') or '/vault/'
        login_url = f"/login/?next={referer}"
        if prod_id:
            login_url += f"&wishlist_add={prod_id}"
        return JsonResponse({
            'success': False,
            'requires_login': True,
            'login_url': login_url,
            'message': 'Please sign in to save pieces to your private wishlist folio.'
        }, status=401)
    
    user_wishlist = request.session.get('user_wishlist', [])
    is_saved = True
    if prod_id:
        p_val = int(prod_id) if str(prod_id).isdigit() else prod_id
        if p_val in user_wishlist:
            user_wishlist.remove(p_val)
            is_saved = False
        else:
            user_wishlist.append(p_val)
            is_saved = True
        request.session['user_wishlist'] = user_wishlist

    return JsonResponse({
        'success': True,
        'is_wishlisted': is_saved,
        'count': len(user_wishlist),
        'message': 'Piece saved to your private wishlist' if is_saved else 'Piece removed from wishlist'
    })


def customer_login_view(request):
    from django.contrib.auth import authenticate, login
    from cart.services import get_or_create_cart
    from .models import AuthRateLimitLog

    next_url = get_safe_redirect(request)
    
    if request.user.is_authenticated:
        return redirect(next_url)

    error = None
    success_msg = None
    identifier = ''
    remember_me = False

    if request.GET.get('reset_success'):
        success_msg = "Your confidential password has been reset. Please sign in with your new password."

    if request.method == 'POST':
        identifier = str(request.POST.get('identifier', '')).strip()
        password = str(request.POST.get('password', '')).strip()
        remember_me = bool(request.POST.get('remember_me'))
        ip = get_client_ip(request)

        # IP-level rate limiting: max 15 requests per 10 minutes
        if AuthRateLimitLog.is_rate_limited(ip, 'login', max_requests=15, window_seconds=600):
            error = "Too many login attempts from your network. Please wait a few moments before trying again."
        elif not identifier or not password:
            error = "Please provide both your email (or mobile number) and password."
        else:
            user = authenticate(request, username=identifier, password=password)
            if user is not None:
                old_key = request.session.session_key
                login(request, user)
                request.session.cycle_key()
                request.session['guest_session_key'] = old_key

                # Session duration: 2 weeks with "Remember me", otherwise until browser closes
                if remember_me:
                    request.session.set_expiry(14 * 24 * 60 * 60)
                else:
                    request.session.set_expiry(0)

                # Merge guest cart into customer's saved cart (enforcing no duplicates and 1-of-a-kind limits)
                get_or_create_cart(request)

                # Check pending wishlist addition
                wishlist_add = request.GET.get('wishlist_add')
                if wishlist_add:
                    wl = request.session.get('user_wishlist', [])
                    p_val = int(wishlist_add) if str(wishlist_add).isdigit() else wishlist_add
                    if p_val not in wl:
                        wl.append(p_val)
                        request.session['user_wishlist'] = wl

                return redirect(next_url)
            else:
                if getattr(request, 'account_locked', False):
                    mins = getattr(request, 'locked_minutes', 15)
                    error = f"Too many incorrect attempts. Your account is temporarily locked for {mins} minutes for your security."
                else:
                    AuthRateLimitLog.record(ip, 'login', identifier)
                    # Constant error message to prevent enumeration
                    error = "Incorrect email or password."

    return render(request, 'campaigns/login.html', {
        'next': next_url,
        'error': error,
        'success_msg': success_msg,
        'identifier': identifier,
        'remember_me': remember_me,
    })


def customer_signup_view(request):
    from django.contrib.auth import login
    from django.contrib.auth.models import User
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    from cart.services import get_or_create_cart
    from notifications.emails import send_verification_email
    from .models import UserProfile, AuthRateLimitLog

    next_url = get_safe_redirect(request)
    if request.user.is_authenticated:
        return redirect(next_url)

    error = None
    full_name = ''
    email = ''
    mobile_number = ''
    terms_consent = False

    if request.method == 'POST':
        full_name = str(request.POST.get('full_name', '')).strip()
        email = str(request.POST.get('email', '')).strip().lower()
        mobile_raw = str(request.POST.get('mobile_number', '')).strip()
        password = str(request.POST.get('password', '')).strip()
        confirm_password = str(request.POST.get('confirm_password', '')).strip()
        terms_consent = bool(request.POST.get('terms_consent'))
        ip = get_client_ip(request)

        # Clean mobile number
        clean_phone = mobile_raw.replace(' ', '').replace('-', '')
        if clean_phone.startswith('+91'):
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('0'):
            clean_phone = clean_phone[1:]

        # Rate limiting: max 5 signups per hour per IP
        if AuthRateLimitLog.is_rate_limited(ip, 'signup', max_requests=5, window_seconds=3600):
            error = "Too many account registrations from your network. Please try again later or contact concierge."
        elif not terms_consent:
            error = "Please review and agree to the Terms of Service and Privacy Policy to create your folio."
        elif not full_name:
            error = "Please provide your full name."
        elif not email or '@' not in email:
            error = "Please enter a valid email address."
        elif not clean_phone.isdigit() or len(clean_phone) != 10:
            error = "Please enter a valid 10-digit Indian mobile number."
        elif password != confirm_password:
            error = "The entered passwords do not match."
        else:
            temp_user = User(username=email, email=email, first_name=full_name)
            try:
                validate_password(password, user=temp_user)
            except ValidationError as ve:
                error = " ".join(ve.messages)

            if not error and User.objects.filter(email__iexact=email).exists():
                error = "An account with this email address already exists. Please sign in or reset your password."

            if not error and UserProfile.objects.filter(mobile_number=clean_phone).exists():
                error = "An account with this mobile number already exists. Please sign in."

            if not error:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=full_name
                )
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.mobile_number = clean_phone
                profile.is_email_verified = True
                profile.save()

                AuthRateLimitLog.record(ip, 'signup', email)
                try:
                    from notifications.emails import send_welcome_email
                    send_welcome_email(user)
                except Exception:
                    pass

                # Log user in directly with active session and merged bag
                old_key = request.session.session_key
                login(request, user, backend='campaigns.auth_backends.EmailOrPhoneBackend')
                request.session.cycle_key()
                request.session['guest_session_key'] = old_key
                request.session.set_expiry(14 * 24 * 60 * 60)
                get_or_create_cart(request)

                target_redirect = next_url if next_url and next_url != '/' else '/'
                return redirect(target_redirect)

    return render(request, 'campaigns/signup.html', {
        'next': next_url,
        'error': error,
        'full_name': full_name,
        'email': email,
        'mobile_number': mobile_number,
        'terms_consent': terms_consent,
    })


def forgot_password_view(request):
    from django.contrib.auth.models import User
    from notifications.emails import send_password_reset_email
    from .models import AuthRateLimitLog

    dispatched = False
    if request.method == 'POST':
        email = str(request.POST.get('email', '')).strip().lower()
        ip = get_client_ip(request)

        # Rate limiting: max 5 requests per 15 minutes per IP
        if not AuthRateLimitLog.is_rate_limited(ip, 'forgot_password', max_requests=5, window_seconds=900):
            AuthRateLimitLog.record(ip, 'forgot_password', email)
            user = User.objects.filter(email__iexact=email).first()
            if user:
                send_password_reset_email(user, request)

        # Always show constant response to prevent account enumeration
        dispatched = True

    return render(request, 'campaigns/forgot_password.html', {'dispatched': dispatched})


def password_reset_confirm_view(request, uidb64, token):
    from django.contrib.auth.models import User
    from django.contrib.auth.tokens import default_token_generator
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str
    from django.contrib.sessions.models import Session
    from notifications.emails import send_password_changed_notification

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if not user or not default_token_generator.check_token(user, token):
        return render(request, 'campaigns/password_reset.html', {
            'error': 'This password reset link has expired or has already been used. Please request a new link.'
        })

    error = None
    if request.method == 'POST':
        new_password = str(request.POST.get('password', '')).strip()
        confirm_password = str(request.POST.get('confirm_password', '')).strip()

        if new_password != confirm_password:
            error = "The new passwords entered do not match."
        else:
            try:
                validate_password(new_password, user=user)
            except ValidationError as ve:
                error = " ".join(ve.messages)

            if not error:
                user.set_password(new_password)
                user.save()

                # Invalidate all other active sessions across devices
                user_pk_str = str(user.pk)
                for s in Session.objects.all():
                    try:
                        data = s.get_decoded()
                        if str(data.get('_auth_user_id')) == user_pk_str:
                            s.delete()
                    except Exception:
                        pass

                if hasattr(user, 'profile'):
                    user.profile.reset_failed_attempts()

                send_password_changed_notification(user)
                return redirect('/login/?reset_success=1')

    return render(request, 'campaigns/password_reset.html', {'error': error})


def verify_email_view(request, uidb64, token):
    from django.contrib.auth.models import User
    from django.contrib.auth.tokens import default_token_generator
    from django.contrib.auth import login
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str
    from notifications.emails import send_welcome_email
    from .models import UserProfile

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_email_verified = True
        profile.save(update_fields=['is_email_verified'])

        # Auto-login if not logged in as this user
        if not request.user.is_authenticated or request.user.pk != user.pk:
            login(request, user, backend='campaigns.auth_backends.EmailOrPhoneBackend')
            request.session.cycle_key()

        send_welcome_email(user)
        next_url = request.session.pop('checkout_next_url', None) or '/orders/checkout/'
        return render(request, 'campaigns/verify_email.html', {
            'success': True,
            'redirect_url': next_url,
            'user': user,
        })
    else:
        user_email = user.email if user else ''
        return render(request, 'campaigns/verify_email.html', {
            'success': False,
            'user_email': user_email,
        })


def verify_email_pending_view(request):
    next_url = get_safe_redirect(request)
    return redirect(next_url)


def resend_verification_email_view(request):
    from django.contrib.auth.models import User
    from django.contrib import messages
    from django.utils import timezone
    from notifications.emails import send_verification_email
    from .models import UserProfile

    if request.method != 'POST':
        return redirect('/verify-email/pending/')

    email = str(request.POST.get('email', '')).strip().lower()
    next_url = request.POST.get('next') or '/orders/checkout/'

    user = None
    if request.user.is_authenticated:
        user = request.user
    elif email:
        user = User.objects.filter(email__iexact=email).first()

    if not user:
        messages.error(request, "Account not found. Please sign up or log in first.")
        return redirect('/signup/')

    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Rate-limiting: maximum 3 resends per hour
    now = timezone.now()
    one_hour_ago = now - timezone.timedelta(hours=1)

    if profile.last_resend_at and profile.last_resend_at > one_hour_ago and profile.resend_verification_count >= 3:
        messages.error(request, "Maximum limit of 3 verification emails per hour reached. Please check your spam folder or try again in 1 hour.")
        return redirect(f"/verify-email/pending/?next={next_url}")

    if not profile.last_resend_at or profile.last_resend_at <= one_hour_ago:
        profile.resend_verification_count = 1
    else:
        profile.resend_verification_count += 1

    profile.last_resend_at = now
    profile.save(update_fields=['resend_verification_count', 'last_resend_at'])

    send_verification_email(user, request)
    messages.success(request, f"A fresh verification email has been sent to {user.email}. Link valid for 1 hour.")
    return redirect(f"/verify-email/pending/?next={next_url}")


def account_profile_view(request):
    from django.contrib.auth.decorators import login_required
    from orders.models import Order
    from .models import UserProfile

    if not request.user.is_authenticated:
        return redirect(f"/login/?next=/account/profile/")

    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    success_msg = None
    error_msg = None

    if request.method == 'POST':
        first_name = str(request.POST.get('first_name', '')).strip()
        mobile_number = str(request.POST.get('mobile_number', '')).strip().replace(' ', '').replace('-', '')
        if mobile_number.startswith('+91'):
            mobile_number = mobile_number[3:]

        if first_name:
            user.first_name = first_name
            user.save(update_fields=['first_name'])

        if mobile_number and len(mobile_number) == 10 and mobile_number.isdigit():
            existing = UserProfile.objects.filter(mobile_number=mobile_number).exclude(user=user).first()
            if existing:
                error_msg = "This mobile number is already linked to another client folio."
            else:
                profile.mobile_number = mobile_number
                profile.save(update_fields=['mobile_number'])
                success_msg = "Your personal client folio details have been updated."
        elif mobile_number:
            error_msg = "Please provide a valid 10-digit mobile number."
        else:
            success_msg = "Your personal client folio details have been updated."

    order_count = Order.objects.filter(user=user).count()

    return render(request, 'campaigns/account/profile.html', {
        'user': user,
        'order_count': order_count,
        'active_tab': 'profile',
        'success_msg': success_msg,
        'error_msg': error_msg,
    })


def account_change_password_view(request):
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    from notifications.emails import send_password_changed_notification

    if not request.user.is_authenticated:
        return redirect(f"/login/?next=/account/password/")

    user = request.user
    success_msg = None
    error_msg = None

    if request.method == 'POST':
        current_password = str(request.POST.get('current_password', '')).strip()
        new_password = str(request.POST.get('new_password', '')).strip()
        confirm_password = str(request.POST.get('confirm_password', '')).strip()

        if not user.check_password(current_password):
            error_msg = "The current password entered is incorrect."
        elif new_password != confirm_password:
            error_msg = "The new password and confirmation password do not match."
        else:
            try:
                validate_password(new_password, user=user)
            except ValidationError as ve:
                error_msg = " ".join(ve.messages)

            if not error_msg:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                send_password_changed_notification(user)
                success_msg = "Your confidential password has been updated successfully."

    return render(request, 'campaigns/account/change_password.html', {
        'user': user,
        'active_tab': 'password',
        'success_msg': success_msg,
        'error_msg': error_msg,
    })


def account_addresses_view(request):
    from orders.models import ShippingAddress

    if not request.user.is_authenticated:
        return redirect(f"/login/?next=/account/addresses/")

    user = request.user
    success_msg = None
    error_msg = None

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_address':
            full_name = str(request.POST.get('full_name', '')).strip()
            phone = str(request.POST.get('phone', '')).strip()
            address_line1 = str(request.POST.get('address_line1', '')).strip()
            address_line2 = str(request.POST.get('address_line2', '')).strip()
            city = str(request.POST.get('city', '')).strip()
            state = str(request.POST.get('state', '')).strip()
            pincode = str(request.POST.get('pincode', '')).strip()

            if not full_name or not phone or not address_line1 or not pincode:
                error_msg = "Please fill in all required address fields."
            else:
                ShippingAddress.objects.create(
                    user=user,
                    full_name=full_name,
                    phone=phone,
                    email=user.email,
                    address_line1=address_line1,
                    address_line2=address_line2,
                    city=city or 'Surat',
                    state=state or 'Gujarat',
                    pincode=pincode,
                )
                success_msg = "Verified delivery address saved to your folio."
        elif action == 'delete_address':
            addr_id = request.POST.get('address_id')
            ShippingAddress.objects.filter(id=addr_id, user=user).delete()
            success_msg = "Address removed from your folio."

    addresses = ShippingAddress.objects.filter(user=user).order_by('-id')

    return render(request, 'campaigns/account/addresses.html', {
        'user': user,
        'addresses': addresses,
        'active_tab': 'addresses',
        'success_msg': success_msg,
        'error_msg': error_msg,
    })


def customer_logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    request.session.flush()
    return redirect('campaigns:hero')


def privacy_policy_view(request):
    """
    Renders the Atelier Nilaya Privacy Policy page satisfying the IT Act 2000 / SPDI Rules 2011
    and Digital Personal Data Protection Act 2023 / DPDP Rules 2025.
    """
    return render(request, 'campaigns/privacy_policy.html', {
        'page_title': 'Privacy Policy — Atelier Nilaya',
        'meta_description': 'Privacy Policy for Atelier Nilaya, Surat. Learn how we handle your personal data, order records, and privacy rights under Indian data protection laws.',
    })


def terms_of_provenance_view(request):
    """
    Renders the Atelier Nilaya Terms of Provenance (Terms & Conditions) covering BIS Hallmarking,
    6-digit HUID, gemstone disclosures, pricing formula, insured shipping, and lifetime buyback.
    """
    return render(request, 'campaigns/terms_of_provenance.html', {
        'page_title': 'Terms of Provenance — Atelier Nilaya',
        'meta_description': 'Terms of Provenance and sales conditions for Atelier Nilaya, Surat. Bureau of Indian Standards (BIS) hallmarking, HUID authenticity, insured transit, and client guarantees.',
    })



