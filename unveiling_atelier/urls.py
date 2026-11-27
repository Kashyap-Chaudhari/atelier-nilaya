import os
import sys
import traceback
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseServerError

from orders.views import checkout_view

site_mode = os.environ.get('SITE_MODE', 'store').lower()

if site_mode == 'admin':
    # Dedicated Standalone Admin Portal Deployment
    urlpatterns = [
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

from django.urls import re_path
from django.views.static import serve

# Route media files (campaign videos, high-res posters, brand assets) in both dev and production
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

def custom_500(request):
    """Diagnostic 500 handler to log traceback to Vercel console and show exact cause."""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback) if exc_type else []
    tb_text = "".join(tb_lines)
    print("=" * 60, file=sys.stderr)
    print("500 INTERNAL SERVER ERROR DIAGNOSTIC:", file=sys.stderr)
    print(tb_text if tb_text else "No active exception found in sys.exc_info()", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    html = f"""<!DOCTYPE html>
<html>
<head><title>Server Configuration Diagnostic (500)</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #FAF7F2; color: #2C2A29; padding: 2rem; margin: 0; }}
.card {{ max-width: 800px; margin: 0 auto; background: #fff; padding: 2rem; border-radius: 8px; border: 1px solid #E5DCCF; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
h1 {{ color: #642D3B; font-size: 1.5rem; margin-top: 0; }}
pre {{ background: #2D2426; color: #F5EFEB; padding: 1rem; border-radius: 6px; overflow-x: auto; font-size: 0.85rem; line-height: 1.4; }}
.tip {{ background: #F5EFEB; border-left: 4px solid #B8893B; padding: 0.75rem 1rem; margin-top: 1rem; font-size: 0.9rem; }}
</style>
</head>
<body>
<div class="card">
    <h1>Atelier Nilaya — Server Diagnostic</h1>
    <p>A server error occurred while handling this request. Below is the active system diagnostic:</p>
    <pre>{tb_text if tb_text else 'No exception traceback captured. Ensure DATABASE_URL is set in Vercel Environment Variables.'}</pre>
    <div class="tip">
        <strong>Common Fix:</strong> If this mentions a database or connection error, check that <code>DATABASE_URL</code> is added in your Vercel Project Settings &rarr; Environment Variables.
    </div>
</div>
</body>
</html>"""
    return HttpResponseServerError(html)

handler500 = custom_500
