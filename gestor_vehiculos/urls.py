# Código corregido para asignacion_api/gestor_vehiculos/urls.py

from django.contrib import admin
from django.urls import path, include
# 1. Importaciones necesarias para servir archivos multimedia
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from asignaciones.views import UserGroupView

@csrf_exempt
def health_check(request):
    """Vista simple para healthcheck de Railway"""
    return JsonResponse({
        'status': 'healthy', 
        'message': 'API is running',
        'debug': settings.DEBUG,
        'version': '1.0.0'
    })

@csrf_exempt 
def api_info(request):
    """Vista de información de la API"""
    return JsonResponse({
        'name': 'SSVQ API',
        'version': '1.0.0',
        'description': 'API para gestión de vehículos y asignaciones',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'user_groups': '/api/user-groups/',
        }
    })

urlpatterns = [
    path('', health_check, name='health-check'),  # Ruta raíz para healthcheck
    path('info/', api_info, name='api-info'),  # Información de la API
    path('admin/', admin.site.urls),
    path('api/', include('asignaciones.urls')),
    path('api/user-groups/', UserGroupView.as_view(), name='user-groups'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 2. Añade esta condición al final del archivo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)