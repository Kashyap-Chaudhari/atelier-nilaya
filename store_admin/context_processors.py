from .models import StoreSettings, ThemeSettings, HeaderMenuItem, FooterColumn

def store_admin_context(request):
    """
    Supplies dynamic, database-driven website settings, theme variables,
    navigation menus, and admin authorization flags to all storefront templates.
    """
    settings = StoreSettings.get_settings()
    theme = ThemeSettings.get_theme()
    
    # Check if the current viewer is a logged-in admin staff member
    is_admin = False
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            is_admin = True
        elif hasattr(request.user, 'admin_profile') and request.user.admin_profile.is_active_staff:
            is_admin = True

    header_menus = HeaderMenuItem.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children').order_by('display_order')
    footer_cols = FooterColumn.objects.filter(is_active=True).prefetch_related('links').order_by('display_order')

    return {
        'store_settings': settings,
        'store_theme': theme,
        'header_menus': header_menus,
        'footer_columns': footer_cols,
        'is_store_admin': is_admin,
    }
