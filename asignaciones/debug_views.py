from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
def debug_info(request):
    """
    Vista temporal para debugging - eliminar en producción
    """
    info = {
        'environment_variables': {
            'DEBUG': os.environ.get('DEBUG', 'NOT SET'),
            'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT', 'NOT SET'),
            'RAILWAY_PUBLIC_DOMAIN': os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'NOT SET'),
        },
        'request_info': {
            'is_secure': request.is_secure(),
            'scheme': getattr(request, 'scheme', 'NOT SET'),
            'host': request.get_host(),
            'x_forwarded_proto': request.META.get('HTTP_X_FORWARDED_PROTO', 'NOT SET'),
        },
        'django_settings': {
            'DEBUG': getattr(__import__('django.conf').conf.settings, 'DEBUG', 'NOT SET'),
            'SECURE_SSL_REDIRECT': getattr(__import__('django.conf').conf.settings, 'SECURE_SSL_REDIRECT', 'NOT SET'),
            'USE_TLS': getattr(__import__('django.conf').conf.settings, 'USE_TLS', 'NOT SET'),
        }
    }
    
    return JsonResponse(info, indent=2)
