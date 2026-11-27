import logging
from .models import StoreSettings, ThemeSettings, HeaderMenuItem, FooterColumn

logger = logging.getLogger(__name__)

def store_admin_context(request):
    """
    Supplies dynamic, database-driven website settings, theme variables,
    navigation menus, and admin authorization flags to all storefront templates.
    """
    try:
        settings = StoreSettings.get_settings()
        theme = ThemeSettings.get_theme()
    except Exception as e:
        logger.warning(f"Could not load store settings/theme from DB: {e}")
        settings = None
        theme = None

    # Check if the current viewer is a logged-in admin staff member
    is_admin = False
    try:
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                is_admin = True
            elif hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_active_staff:
                is_admin = True
    except Exception as e:
        logger.warning(f"Could not check admin profile: {e}")

    try:
        header_menus = HeaderMenuItem.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children').order_by('display_order')
        footer_cols = FooterColumn.objects.filter(is_active=True).prefetch_related('links').order_by('display_order')
    except Exception as e:
        logger.warning(f"Could not load navigation menus from DB: {e}")
        header_menus = []
        footer_cols = []

    return {
        'store_settings': settings,
        'store_theme': theme,
        'header_menus': header_menus,
        'footer_columns': footer_cols,
        'is_store_admin': is_admin,
    }
