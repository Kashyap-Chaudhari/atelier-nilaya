from django.urls import path
from django.shortcuts import redirect
from .views import (
    HeroAtelierView,
    CampaignDetailView,
    campaigns_api,
    CategoryProductListView,
    AllProductsVaultView,
    ProductDetailView,
    WishlistView,
    api_cart_django,
    api_wishlist_toggle_django,
    customer_login_view,
    customer_signup_view,
    customer_logout_view,
    forgot_password_view,
    password_reset_confirm_view,
    verify_email_view,
    verify_email_pending_view,
    resend_verification_email_view,
    account_profile_view,
    account_change_password_view,
    account_addresses_view,
    privacy_policy_view,
    terms_of_provenance_view,
)

app_name = 'campaigns'

urlpatterns = [
    # Statutory Legal & Compliance Pages
    path('privacy-policy/', privacy_policy_view, name='privacy_policy'),
    path('terms-of-provenance/', terms_of_provenance_view, name='terms_of_provenance'),

    # Core Production Authentication Suite
    path('login/', customer_login_view, name='login'),
    path('signup/', customer_signup_view, name='signup'),
    path('logout/', customer_logout_view, name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset/<str:uidb64>/<str:token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('verify-email/pending/', verify_email_pending_view, name='verify_email_pending'),
    path('verify-email/resend/', resend_verification_email_view, name='resend_verification_email'),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email_view, name='verify_email'),

    # Account Folio Pages
    path('account/', lambda r: redirect('campaigns:account_profile'), name='account_index'),
    path('account/profile/', account_profile_view, name='account_profile'),
    path('account/password/', account_change_password_view, name='account_password'),
    path('account/addresses/', account_addresses_view, name='account_addresses'),
    path('account/orders/', lambda r: redirect('orders:history'), name='account_orders'),

    # Boutique Catalog & Cart/Wishlist
    path('', HeroAtelierView.as_view(), name='hero'),
    path('category/<slug:slug>/', CategoryProductListView.as_view(), name='category_products'),
    path('c/<slug:slug>/', CategoryProductListView.as_view(), name='cat_short'),
    path('p/<slug:slug>/', ProductDetailView.as_view(), name='product_detail_slug'),
    path('p/<slug:slug>', ProductDetailView.as_view(), name='product_detail_slug_noslash'),
    path('p/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail_long'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('vault/', AllProductsVaultView.as_view(), name='vault'),
    path('collection/<slug:slug>/', CampaignDetailView.as_view(), name='detail'),
    path('api/campaigns/', campaigns_api, name='api_campaigns'),
    path('api/cart/', api_cart_django, name='api_cart'),
    path('api/cart', api_cart_django, name='api_cart_no_slash'),
    path('api/wishlist/toggle', api_wishlist_toggle_django, name='api_wishlist_toggle'),
]
