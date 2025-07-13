"""
Middleware para forzar HTTPS en URLs generadas por Django REST Framework
"""

class ForceHTTPSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Force HTTPS for production environment
        if (hasattr(request, 'META') and 
            'HTTP_X_FORWARDED_PROTO' in request.META and 
            request.META['HTTP_X_FORWARDED_PROTO'] == 'https'):
            request.is_secure = lambda: True
        
        # Check for Railway environment or other production indicators
        import os
        if 'RAILWAY_ENVIRONMENT' in os.environ or os.environ.get('DEBUG', 'True').lower() == 'false':
            request.is_secure = lambda: True
            
        response = self.get_response(request)
        return response
