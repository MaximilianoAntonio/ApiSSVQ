"""
Middleware personalizado para Railway
"""
from django.utils.deprecation import MiddlewareMixin
import os

class RailwayMiddleware(MiddlewareMixin):
    """
    Middleware para manejar configuraciones específicas de Railway
    """
    
    def process_request(self, request):
        # Agregar headers para Railway
        if 'railway.app' in request.get_host():
            # Configurar CSRF trusted origins dinámicamente
            from django.conf import settings
            current_host = f"https://{request.get_host()}"
            
            if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
                if current_host not in settings.CSRF_TRUSTED_ORIGINS:
                    settings.CSRF_TRUSTED_ORIGINS.append(current_host)
            else:
                settings.CSRF_TRUSTED_ORIGINS = [current_host]
        
        return None
    
    def process_response(self, request, response):
        # Agregar headers de seguridad para Railway
        if not os.environ.get('DEBUG', 'True') == 'True':
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
        
        return response
