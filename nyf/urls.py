from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')), # Include URLs from your 'app'
    # Include Django's built-in auth URLs for password reset
    path('accounts/', include('django.contrib.auth.urls')), # This adds urls like /accounts/password_reset/, etc.
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)