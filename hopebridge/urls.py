"""
URL configuration for hopebridge project.
"""
import importlib.util
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin (kept for emergency/superadmin access)
    path('django-admin/', admin.site.urls),

    # Local apps
    path('', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('donors/', include('donors.urls')),
    path('donate/', include('donations.urls')),
    path('drives/', include('drives.urls')),
    path('events/', include('events.urls')),
    path('programs/', include('programs.urls')),
    path('volunteers/', include('volunteers.urls')),
    path('invoices/', include('invoices.urls')),
    path('notifications/', include('notifications.urls')),
    path('admin-panel/', include('custom_admin.urls')),
]

# Conditionally include allauth URLs if allauth is installed
if importlib.util.find_spec('allauth'):
    urlpatterns.append(path('accounts/social/', include('allauth.urls')))

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
