"""
WSGI config for unveiling_atelier project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unveiling_atelier.settings')

application = get_wsgi_application()

try:
    from whitenoise import WhiteNoise
    # Wrap WSGI application with WhiteNoise to reliably stream static and media (videos/posters) on Vercel
    static_root = str(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else os.path.join(settings.BASE_DIR, 'staticfiles')
    media_root = str(settings.MEDIA_ROOT) if hasattr(settings, 'MEDIA_ROOT') else os.path.join(settings.BASE_DIR, 'media')
    
    application = WhiteNoise(application, root=static_root, prefix=settings.STATIC_URL)
    if os.path.isdir(media_root):
        application.add_files(media_root, prefix=settings.MEDIA_URL)
except Exception as e:
    import sys
    print(f"WhiteNoise WSGI setup notice: {e}", file=sys.stderr)

app = application
