from django.http import JsonResponse
from django.views import View
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class HealthCheckView(View):
    """
    Health check endpoint for Azure App Service
    """
    def get(self, request):
        try:
            # Basic health check
            response_data = {
                'status': 'healthy',
                'service': 'gestor-vehiculos-api',
                'timestamp': str(timezone.now())
            }
            return JsonResponse(response_data, status=200)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e)
            }, status=500)
