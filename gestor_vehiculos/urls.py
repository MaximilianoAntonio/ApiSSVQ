# Código corregido para asignacion_api/gestor_vehiculos/urls.py

from django.contrib import admin
from django.urls import path, include
# 1. Importaciones necesarias para servir archivos multimedia
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from asignaciones.views import UserGroupView

def health_check(request):
    """Simple health check endpoint for Railway"""
    return JsonResponse({"status": "healthy", "message": "Django app is running"})

urlpatterns = [
    path('', health_check, name='health-check'),  # Root path health check
    path('health/', health_check, name='health'),  # Explicit health endpoint
    path('admin/', admin.site.urls),
    path('api/', include('asignaciones.urls')),
    path('api/user-groups/', UserGroupView.as_view(), name='user-groups'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 2. Añade esta condición al final del archivo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)