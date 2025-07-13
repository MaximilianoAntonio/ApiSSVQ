# 🔍 DIAGNÓSTICO RAILWAY ERROR 500 - SIN TOCAR BASE DE DATOS

## Problemas Potenciales (manteniendo tu configuración MSSQL):

### 1. 🔴 **IMPORTS FALTANTES EN VIEWS.PY**

Revisando tu código, veo que falta este import crítico:

```python
# EN asignaciones/views.py línea 11, agregar:
from django.db.models import Count, Q, Avg, Sum, Case, When, IntegerField
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate, Extract
```

### 2. 🟡 **VARIABLES DE ENTORNO FALTANTES**

En Railway, estas variables podrían no estar configuradas:
- `SECRET_KEY` (crítico)
- `DEBUG` (debería ser False)
- Variables de tu base de datos MSSQL

### 3. 🟡 **PROBLEMA CON DEPENDENCIES**

En requirements.txt, verifica que tengas:
```txt
django-extensions  # Necesario para tu INSTALLED_APPS
django-filter     # Para DjangoFilterBackend
```

### 4. 🟡 **ALLOWED_HOSTS**

En settings.py, asegúrate que incluya tu dominio de Railway:
```python
ALLOWED_HOSTS = [
    '*',  # O específicamente tu dominio de Railway
    'tu-app.railway.app',
]
```

### 5. 🔴 **POSIBLE ERROR EN DASHBOARD CODE**

Tu DashboardStatsView podría tener un bug. Veo que usas métodos como:
- `_get_general_stats()`
- `_get_vehiculos_stats()`
- `_get_conductores_stats()`

Si alguno de estos métodos falla, causaría error 500.

## ✅ SOLUCIONES RÁPIDAS (SIN TOCAR DB):

### 1. AGREGAR IMPORTS FALTANTES
```python
# Al inicio de asignaciones/views.py, después de la línea 12:
from django.db.models import Count, Q, Avg, Sum, Case, When, IntegerField
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate, Extract
```

### 2. VERIFICAR VARIABLES EN RAILWAY
En Railway Dashboard → Settings → Variables:
```
SECRET_KEY=tu-clave-secreta-actual
DEBUG=False
AZURE_SQL_NAME=ssvq
AZURE_SQL_USER=ssvqdb@ssvq
AZURE_SQL_HOST=ssvq.database.windows.net
AZURE_SQL_PORT=1433
```

### 3. AGREGAR LOGGING TEMPORAL
En settings.py, al final:
```python
# Logging para debug en Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'asignaciones': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 4. SIMPLIFICAR DASHBOARD TEMPORALMENTE
Crear una versión simple del dashboard para probar:

```python
class DashboardStatsViewSimple(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Estadísticas básicas sin métodos complejos
            total_vehiculos = Vehiculo.objects.count()
            total_conductores = Conductor.objects.count()
            total_asignaciones = Asignacion.objects.count()
            
            data = {
                'basic_stats': {
                    'vehiculos': total_vehiculos,
                    'conductores': total_conductores,
                    'asignaciones': total_asignaciones,
                    'timestamp': timezone.now().isoformat()
                }
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            return Response({
                'error': str(e),
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

## 🔧 CAMBIOS MÍNIMOS NECESARIOS:

### ARCHIVO 1: asignaciones/views.py
Agregar imports faltantes (línea 12):
```python
from django.db.models import Count, Q, Avg, Sum, Case, When, IntegerField
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate, Extract
```

### ARCHIVO 2: asignaciones/urls.py
Si quieres probar la versión simple:
```python
# Agregar esta línea en urlpatterns:
path('dashboard/simple/', DashboardStatsViewSimple.as_view(), name='dashboard-simple'),
```

### ARCHIVO 3: requirements.txt
Verificar que tengas:
```txt
django-extensions
django-filter
```

## 🚀 PASOS PARA CORREGIR:

1. **Agregar imports faltantes** en views.py
2. **Configurar variables de entorno** en Railway
3. **Agregar logging** para ver errores específicos
4. **Commit y push**
5. **Ver logs en Railway** para identificar el error exacto

## 🔍 DEBUGGING:

Después del deploy, ver logs en:
Railway Dashboard → tu proyecto → Deployments → Runtime Logs

Los logs te dirán exactamente qué está fallando.

¿Cuál de estos pasos quieres que implemente primero?
