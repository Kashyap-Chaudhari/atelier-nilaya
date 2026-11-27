from django.urls import path
from .views.auth_views import admin_login_view, admin_logout_view, admin_profile_view
from .views.dashboard_views import dashboard_view, global_search_api
from .views.order_views import (
    order_list_view, order_detail_view, order_update_status_view,
    order_invoice_view, order_packing_slip_view
)
from .views.product_views import (
    product_list_view, product_create_view, product_edit_view,
    product_duplicate_view, product_delete_view, product_export_csv_view
)
from .views.content_views import (
    homepage_builder_view, featured_edit_builder_view,
    pages_list_view, page_edit_view
)
from .views.customer_views import customer_list_view, customer_detail_view
from .views.settings_views import (
    settings_brand_view, settings_theme_view, settings_header_footer_view,
    settings_shipping_view, settings_taxes_view, settings_emails_view
)
from .views.audit_views import audit_log_view, trash_bin_view

app_name = 'store_admin'

urlpatterns = [
    # Dashboard & Global Search
    path('', dashboard_view, name='dashboard'),
    path('api/search/', global_search_api, name='api_search'),

    # Authentication & Profile
    path('login/', admin_login_view, name='login'),
    path('logout/', admin_logout_view, name='logout'),
    path('profile/', admin_profile_view, name='profile'),

    # Orders Module
    path('orders/', order_list_view, name='order_list'),
    path('orders/<str:order_number>/', order_detail_view, name='order_detail'),
    path('orders/<str:order_number>/status/', order_update_status_view, name='order_status_update'),
    path('orders/<str:order_number>/invoice/', order_invoice_view, name='order_invoice'),
    path('orders/<str:order_number>/packing-slip/', order_packing_slip_view, name='order_packing_slip'),

    # Products Module
    path('products/', product_list_view, name='product_list'),
    path('products/new/', product_create_view, name='product_create'),
    path('products/<int:product_id>/edit/', product_edit_view, name='product_edit'),
    path('products/<int:product_id>/duplicate/', product_duplicate_view, name='product_duplicate'),
    path('products/<int:product_id>/delete/', product_delete_view, name='product_delete'),
    path('products/export/csv/', product_export_csv_view, name='product_export_csv'),

    # Content & Builders
    path('content/homepage/', homepage_builder_view, name='homepage_builder'),
    path('content/featured-edit/', featured_edit_builder_view, name='featured_edit_builder'),
    path('content/pages/', pages_list_view, name='pages_list'),
    path('content/pages/<slug:slug>/', page_edit_view, name='page_edit'),

    # Customers
    path('customers/', customer_list_view, name='customer_list'),
    path('customers/<int:user_id>/', customer_detail_view, name='customer_detail'),

    # Settings
    path('settings/brand/', settings_brand_view, name='settings_brand'),
    path('settings/theme/', settings_theme_view, name='settings_theme'),
    path('settings/navigation/', settings_header_footer_view, name='settings_navigation'),
    path('settings/shipping/', settings_shipping_view, name='settings_shipping'),
    path('settings/taxes/', settings_taxes_view, name='settings_taxes'),
    path('settings/emails/', settings_emails_view, name='settings_emails'),

    # Audit & Trash
    path('audit/', audit_log_view, name='audit_log'),
    path('trash/', trash_bin_view, name='trash_bin'),
]
