import logging
from django.core.cache import cache
from .models import StoreSettings, ThemeSettings, HeaderMenuItem, FooterColumn

logger = logging.getLogger(__name__)

def store_admin_context(request):
    """
    Supplies dynamic, database-driven website settings, theme variables,
    navigation menus, and admin authorization flags to all storefront templates.
    Uses in-memory caching to prevent 6 repetitive remote DB queries per request.
    """
    # 1. Cached Store & Theme Settings (Cache TTL: 300s)
    cached_globals = cache.get('nilaya_store_globals')
    if cached_globals is None:
        try:
            settings_obj = StoreSettings.get_settings()
            theme_obj = ThemeSettings.get_theme()
            header_menus = list(HeaderMenuItem.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children').order_by('display_order'))
            footer_cols = list(FooterColumn.objects.filter(is_active=True).prefetch_related('links').order_by('display_order'))
            cached_globals = {
                'store_settings': settings_obj,
                'store_theme': theme_obj,
                'header_menus': header_menus,
                'footer_columns': footer_cols,
            }
            cache.set('nilaya_store_globals', cached_globals, timeout=300)
        except Exception as e:
            logger.warning(f"Could not load store settings/theme from DB: {e}")
            cached_globals = {
                'store_settings': None,
                'store_theme': None,
                'header_menus': [],
                'footer_columns': [],
            }

    # 2. Check if the current viewer is a logged-in admin staff member
    is_admin = False
    try:
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                is_admin = True
            elif hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_active_staff:
                is_admin = True
    except Exception as e:
        logger.warning(f"Could not check admin profile: {e}")

    return {
        'store_settings': cached_globals.get('store_settings'),
        'store_theme': cached_globals.get('store_theme'),
        'header_menus': cached_globals.get('header_menus', []),
        'footer_columns': cached_globals.get('footer_columns', []),
        'is_store_admin': is_admin,
    }
