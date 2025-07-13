# ⚡ CHECKLIST RÁPIDO - ERROR 500 RAILWAY

## 🔥 CAUSAS MÁS COMUNES (sin tocar DB):

### 1. ✅ **VARIABLES DE ENTORNO FALTANTES**
En Railway Dashboard → Settings → Variables, verifica que tengas:
```
SECRET_KEY=tu-clave-secreta-actual
DEBUG=False
AZURE_SQL_NAME=ssvq
AZURE_SQL_USER=ssvqdb@ssvq
AZURE_SQL_PASSWORD=ssvq1!flota
AZURE_SQL_HOST=ssvq.database.windows.net
AZURE_SQL_PORT=1433
```

### 2. ✅ **ALLOWED_HOSTS INCORRECTO**
En settings.py, verifica:
```python
ALLOWED_HOSTS = ['*']  # O tu dominio específico de Railway
```

### 3. ✅ **IMPORTS FALTANTES O INCORRECTOS**
Verifica que en requirements.txt tengas:
```txt
django-extensions  # Para INSTALLED_APPS
django-filter      # Para DjangoFilterBackend
mssql-django       # Para tu base de datos MSSQL
pyodbc            # Para conectar a MSSQL
```

### 4. ✅ **MIDDLEWARE MAL CONFIGURADO**
En settings.py, verifica el orden:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Debe estar aquí
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... resto del middleware
]
```

### 5. ✅ **STATIC FILES MAL CONFIGURADOS**
En settings.py:
```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

## 🔧 SOLUCIONES RÁPIDAS:

### SOLUCIÓN 1: Agregar logging para ver el error exacto
```python
# Al final de settings.py:
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
}
```

### SOLUCIÓN 2: Crear endpoint de prueba simple
Ya agregué `DashboardStatsViewSafe` que puedes probar en:
```
https://tu-app.railway.app/api/dashboard/stats/safe/
```

### SOLUCIÓN 3: Verificar que el comando de start sea correcto
En railway.json o Procfile:
```json
{
  "start": {
    "command": "gunicorn gestor_vehiculos.wsgi:application --bind 0.0.0.0:$PORT"
  }
}
```

### SOLUCIÓN 4: Probar localmente con configuración de producción
```bash
export DEBUG=False
export SECRET_KEY=tu-clave-secreta
python manage.py check --deploy
python manage.py runserver
```

## 📋 PASOS INMEDIATOS:

1. **Verificar variables de entorno** en Railway Dashboard
2. **Agregar logging** en settings.py
3. **Commit y push** los cambios
4. **Probar endpoint seguro** `/api/dashboard/stats/safe/`
5. **Ver logs de Railway** para identificar error específico

## 🔍 DEBUGGING EN RAILWAY:

1. **Ver logs:**
   - Railway Dashboard → tu proyecto → Deployments
   - Click en el último deployment
   - Ver "Runtime Logs"

2. **Probar endpoints básicos:**
   ```
   https://tu-app.railway.app/admin/
   https://tu-app.railway.app/api/
   https://tu-app.railway.app/api/get-token/
   ```

3. **Si el dashboard falla, probar la versión segura:**
   ```
   https://tu-app.railway.app/api/dashboard/stats/safe/
   ```

## ⚠️ ERRORES TÍPICOS Y SOLUCIONES:

### "Module not found"
- ✅ Verificar requirements.txt
- ✅ Verificar imports en views.py

### "Bad Request (400)"
- ✅ Verificar ALLOWED_HOSTS
- ✅ Verificar CSRF_TRUSTED_ORIGINS

### "Internal Server Error (500)"
- ✅ Verificar SECRET_KEY en variables de entorno
- ✅ Verificar logs específicos
- ✅ Probar endpoint /api/dashboard/stats/safe/

### "Database connection error"
- ✅ Verificar variables AZURE_SQL_* en Railway
- ✅ Verificar que Railway puede conectar a tu Azure SQL

## 🚀 COMANDO PARA DIAGNOSTICAR:

```bash
python diagnose_railway_error.py
```

Este script verificará localmente si hay problemas antes de hacer deploy.

¿Cuál de estos pasos quieres que implemente o necesitas ayuda específica con alguno?
