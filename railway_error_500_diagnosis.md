# Railway Error 500 - Diagnóstico y Soluciones

## Problemas Identificados:

### 1. 🔴 **PROBLEMA CRÍTICO: Base de Datos MSSQL**
```python
# En settings.py línea 126-139
DATABASES = {
    'default': {
        'ENGINE': 'mssql',  # ❌ PROBLEMA
        'NAME': os.environ.get('AZURE_SQL_NAME', 'ssvq'),
        # ...
    }
}
```

**Problema**: Railway no soporta nativamente MSSQL/SQL Server. Necesitas usar PostgreSQL.

### 2. 🟡 **PROBLEMA: Driver ODBC**
- `pyodbc` y `ODBC Driver 18 for SQL Server` no están disponibles en Railway
- Railway utiliza contenedores Linux que no tienen estos drivers

### 3. 🟡 **PROBLEMA: Variables de Entorno**
- Las variables `AZURE_SQL_*` no están configuradas en Railway

## ✅ **SOLUCIONES**

### Solución 1: Migrar a PostgreSQL (RECOMENDADO)

1. **Actualizar requirements.txt:**
```txt
# Remover:
# mssql-django
# pyodbc

# Agregar:
psycopg2-binary
dj-database-url
```

2. **Actualizar settings.py:**
```python
import dj_database_url

# Configuración de base de datos para Railway (PostgreSQL)
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # Producción en Railway
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### Solución 2: Variables de Entorno en Railway

Configurar en Railway Dashboard → Variables:
```
DEBUG=False
SECRET_KEY=tu-secret-key-super-segura-aqui
RAILWAY_ENVIRONMENT=production
```

### Solución 3: Logging para Debugging

Agregar al final de settings.py:
```python
# Logging configuration
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
    },
}
```

### Solución 4: Manejo de Archivos Estáticos

Actualizar settings.py:
```python
# Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files (si usas archivos de imagen)
if os.environ.get('RAILWAY_ENVIRONMENT'):
    # En producción, usar un servicio de almacenamiento externo
    # como Cloudinary o AWS S3
    pass
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 🚀 **PASOS PARA CORREGIR**

### Paso 1: Actualizar Base de Datos
```bash
# 1. Crear backup de datos actuales (si los tienes)
python manage.py dumpdata > data_backup.json

# 2. Actualizar requirements.txt (remover mssql-django, pyodbc)
# 3. Actualizar settings.py con configuración PostgreSQL
# 4. En Railway, agregar PostgreSQL addon
# 5. Hacer migraciones
python manage.py makemigrations
python manage.py migrate

# 6. Cargar datos de backup (si necesario)
python manage.py loaddata data_backup.json
```

### Paso 2: Variables de Entorno en Railway
- Ve a tu proyecto en Railway
- Settings → Variables
- Agregar las variables necesarias

### Paso 3: Deployment
```bash
# Commit y push los cambios
git add .
git commit -m "Fix Railway deployment - migrate to PostgreSQL"
git push origin main
```

## 🔍 **CÓMO DEBUGGEAR**

### Ver logs de Railway:
1. Ve a tu proyecto en Railway
2. Click en "Deployments"
3. Click en el último deployment
4. Ver "Deploy Logs" y "Runtime Logs"

### Comandos útiles para debugging:
```bash
# Verificar conexión a DB
python manage.py dbshell

# Verificar migraciones
python manage.py showmigrations

# Crear superuser
python manage.py createsuperuser

# Verificar configuración
python manage.py check --deploy
```

## ⚠️ **ERRORES COMUNES**

1. **Import Error**: Módulos no encontrados
   - Verificar requirements.txt
   - Verificar que todas las dependencias estén instaladas

2. **Database Connection Error**: 
   - Verificar DATABASE_URL en Railway
   - Verificar que PostgreSQL addon esté agregado

3. **Static Files Error**:
   - Ejecutar `python manage.py collectstatic`
   - Verificar configuración de Whitenoise

4. **Secret Key Error**:
   - Configurar SECRET_KEY en variables de entorno
   - No usar la clave de desarrollo en producción
