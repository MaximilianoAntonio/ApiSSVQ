from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
import os

class HTTPSRouter(DefaultRouter):
    """
    Router personalizado que genera URLs HTTPS para Railway y otros entornos de producción
    """
    def get_api_root_view(self, api_urls=None):
        """
        Return a basic root view.
        """
        api_urls = api_urls or []
        
        class APIRootView(APIView):
            """
            The default basic root view for DefaultRouter
            """
            _ignore_model_permissions = True
            schema = None  # exclude from schema
            
            def get(self, request, *args, **kwargs):
                # Detect if we should use HTTPS
                use_https = (
                    # Check Railway environment
                    'RAILWAY_ENVIRONMENT' in os.environ or
                    # Check if debug is false
                    os.environ.get('DEBUG', 'True').lower() == 'false' or
                    # Check X-Forwarded-Proto header
                    request.META.get('HTTP_X_FORWARDED_PROTO') == 'https' or
                    # Check if request is secure
                    request.is_secure()
                )
                
                ret = {}
                namespace = request.resolver_match.namespace
                for key, url_name in self.api_root_dict.items():
                    if namespace:
                        url_name = namespace + ':' + url_name
                    try:
                        url = reverse(
                            url_name,
                            args=args,
                            kwargs=kwargs,
                            request=request,
                            format=kwargs.get('format', None)
                        )
                        
                        # Force HTTPS if in production
                        if use_https and url.startswith('http://'):
                            url = url.replace('http://', 'https://', 1)
                            
                        ret[key] = url
                    except Exception:
                        # Don't fail completely if reverse fails
                        continue
                
                return Response(ret)
        
        return APIRootView.as_view(api_root_dict=self.get_api_root_dict(api_urls))
