"""
Middleware para forzar HTTPS y configurar headers de seguridad
"""

from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class ForceHTTPSMiddleware(MiddlewareMixin):
    """
    Middleware para forzar HTTPS en Azure App Service y corregir URLs de paginación
    """
    
    def process_request(self, request):
        # Corregir el esquema para Azure App Service
        if not settings.DEBUG:
            # Azure App Service usa X-Forwarded-Proto header
            proto = request.META.get('HTTP_X_FORWARDED_PROTO', '')
            if proto == 'https':
                request.is_secure = lambda: True
                request.scheme = 'https'
            elif proto == 'http':
                # Redirigir a HTTPS
                https_url = request.build_absolute_uri().replace('http://', 'https://')
                return HttpResponsePermanentRedirect(https_url)
        
        return None
    
    def process_response(self, request, response):
        # Agregar headers de seguridad para CORS y HTTPS
        if not settings.DEBUG:
            # Permitir CORS pero solo con HTTPS
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response['Access-Control-Allow-Credentials'] = 'true'
            
            # Headers de seguridad
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


class APISecurityMiddleware(MiddlewareMixin):
    """
    Middleware específico para API que agrega headers de seguridad y corrige URLs
    """
    
    def process_response(self, request, response):
        # Solo para rutas de API
        if request.path.startswith('/api/'):
            # Forzar HTTPS en respuestas JSON
            if 'application/json' in response.get('Content-Type', ''):
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                
                # Corregir URLs HTTP en el contenido JSON (para paginación)
                if hasattr(response, 'content') and response.content:
                    try:
                        content = response.content.decode('utf-8')
                        # Reemplazar URLs HTTP por HTTPS en el contenido
                        content = content.replace('http://apissvq.azurewebsites.net', 'https://apissvq.azurewebsites.net')
                        response.content = content.encode('utf-8')
                        response['Content-Length'] = str(len(response.content))
                    except:
                        pass  # Si hay error, no modificar el contenido
        
        return response
