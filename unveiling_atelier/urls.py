import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from orders.views import checkout_view

site_mode = os.environ.get('SITE_MODE', 'store').lower()

if site_mode == 'admin':
    # Dedicated Standalone Admin Portal Deployment
    urlpatterns = [
        path('admin/', include('store_admin.urls')),
        path('', include('store_admin.urls', namespace='store_admin')),
        path('django-admin/', admin.site.urls),
    ]
else:
    # Storefront (and Unified) Deployment
    urlpatterns = [
        path('admin/', include('store_admin.urls', namespace='store_admin')),
        path('django-admin/', admin.site.urls),
        path('checkout/', checkout_view, name='checkout_direct'),
        path('cart/', include('cart.urls', namespace='cart')),
        path('orders/', include('orders.urls', namespace='orders')),
        path('payments/', include('payments.urls', namespace='payments')),
        path('', include('campaigns.urls', namespace='campaigns')),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
