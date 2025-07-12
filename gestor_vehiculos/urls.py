# Código corregido para asignacion_api/gestor_vehiculos/urls.py

from django.contrib import admin
from django.urls import path, include
# 1. Importaciones necesarias para servir archivos multimedia
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from asignaciones.views import UserGroupView

def health_check(request):
    """Vista simple para healthcheck de Railway"""
    return JsonResponse({'status': 'healthy', 'message': 'API is running'})

urlpatterns = [
    path('', health_check, name='health-check'),  # Ruta raíz para healthcheck
    path('admin/', admin.site.urls),
    path('api/', include('asignaciones.urls')),
    path('api/user-groups/', UserGroupView.as_view(), name='user-groups'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 2. Añade esta condición al final del archivo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)