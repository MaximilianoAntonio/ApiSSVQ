"""
Middleware para forzar HTTPS en URLs generadas por Django REST Framework
"""
import os

class ForceHTTPSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Force HTTPS for production environment
        # Check if we're in production (Railway or any other production environment)
        is_production = (
            'RAILWAY_ENVIRONMENT' in os.environ or 
            os.environ.get('DEBUG', 'True').lower() == 'false' or
            'railway.app' in request.get_host() or
            'up.railway.app' in request.get_host()
        )
        
        # Force HTTPS if X-Forwarded-Proto header indicates HTTPS
        if (hasattr(request, 'META') and 
            'HTTP_X_FORWARDED_PROTO' in request.META and 
            request.META['HTTP_X_FORWARDED_PROTO'] == 'https'):
            request.is_secure = lambda: True
        
        # Force HTTPS in production environments
        if is_production:
            request.is_secure = lambda: True
            # Set META for consistent behavior
            request.META['HTTP_X_FORWARDED_PROTO'] = 'https'
            
        response = self.get_response(request)
        return response
