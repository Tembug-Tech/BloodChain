"""
URL configuration for BloodChain project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

def api_root(request):
    """Root API endpoint"""
    return JsonResponse({
        'message': 'BloodChain API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'docs': 'API endpoints available under /api/'
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('donor.urls')),
    path('api/', include('hospital.urls')),
    path('api/', include('blood_tracking.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('rewards.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
