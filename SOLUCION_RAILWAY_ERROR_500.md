# 🚨 SOLUCIÓN RÁPIDA PARA ERROR 500 EN RAILWAY

## El problema principal: **MSSQL no es compatible con Railway**

Railway usa contenedores Linux que no soportan:
- `mssql-django`
- `pyodbc` 
- `ODBC Driver 18 for SQL Server`

## ✅ SOLUCIÓN PASO A PASO

### 1. 🔧 **ACTUALIZAR requirements.txt** (INMEDIATO)

Reemplaza tu `requirements.txt` actual con:

```txt
Django==5.0.6
djangorestframework==3.15.1
psycopg2-binary==2.9.9
dj-database-url==2.1.0
django-cors-headers==4.3.1
django-filter==24.2
django_extensions==3.2.3
djangorestframework-simplejwt==5.3.1
whitenoise==6.7.0
Pillow==10.4.0
gunicorn==22.0.0
requests==2.32.3
pytz==2024.1
Brotli==1.1.0
Faker==25.2.0
asgiref==3.8.1
packaging==24.0
PyJWT==2.8.0
sqlparse==0.5.0
```

### 2. 🔧 **ACTUALIZAR settings.py** (CRÍTICO)

Reemplaza la sección de DATABASES en `gestor_vehiculos/settings.py`:

```python
import dj_database_url

# Detectar entorno Railway
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') is not None

# Configuración de base de datos
if IS_RAILWAY or os.environ.get('DATABASE_URL'):
    # Producción con PostgreSQL
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
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

### 3. 🏗️ **AGREGAR railway.json**

Crear archivo `railway.json` en la raíz:

```json
{
  "build": {
    "command": "python manage.py collectstatic --noinput && python manage.py migrate"
  },
  "start": {
    "command": "gunicorn gestor_vehiculos.wsgi:application --bind 0.0.0.0:$PORT"
  }
}
```

### 4. 🌐 **CONFIGURAR RAILWAY DASHBOARD**

1. Ve a tu proyecto en Railway
2. **Add PostgreSQL addon** (botón + → PostgreSQL)
3. **Variables de entorno** (Settings → Variables):
   ```
   DEBUG=False
   SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-aqui
   RAILWAY_ENVIRONMENT=production
   ```

### 5. 🚀 **DEPLOY**

```bash
git add .
git commit -m "Fix Railway deployment - migrate to PostgreSQL"
git push origin main
```

## 🔍 **VERIFICAR QUE FUNCIONA**

1. **Ver logs de Railway:**
   - Ve a tu proyecto → Deployments → último deployment
   - Revisa "Deploy Logs" y "Runtime Logs"

2. **Probar endpoints:**
   ```bash
   curl https://tu-app.railway.app/api/
   curl https://tu-app.railway.app/api/dashboard/stats/
   ```

## ⚠️ **SI TIENES DATOS EN MSSQL**

### Migrar datos:

1. **Hacer backup de datos actuales:**
   ```bash
   # En tu entorno con MSSQL
   python manage.py dumpdata > backup_data.json
   ```

2. **Después del deploy en Railway:**
   ```bash
   # Cargar datos en PostgreSQL
   python manage.py loaddata backup_data.json
   ```

## 🆘 **SI AÚN HAY ERROR 500**

### Debug en Railway:

1. **Agregar logging temporal** en settings.py:
   ```python
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
           'level': 'DEBUG',
       },
   }
   ```

2. **Ver logs detallados:**
   - Railway Dashboard → tu proyecto → Deployments
   - Click en el deployment más reciente
   - Ver "Runtime Logs"

3. **Comandos útiles para debug:**
   ```bash
   # En Railway CLI o web terminal
   python manage.py check --deploy
   python manage.py showmigrations
   python manage.py dbshell
   ```

## 📞 **ERRORES COMUNES Y SOLUCIONES**

### Error: "No module named 'mssql'"
**Solución:** Actualizar requirements.txt (paso 1)

### Error: "DATABASE_URL not found"
**Solución:** Agregar PostgreSQL addon en Railway

### Error: "Secret key not set"
**Solución:** Configurar SECRET_KEY en variables de entorno

### Error: "Static files not found"
**Solución:** Verificar que railway.json tenga `collectstatic`

## 🎯 **RESUMEN - LO MÁS IMPORTANTE**

1. ✅ **Cambiar de MSSQL a PostgreSQL** (requirements.txt)
2. ✅ **Actualizar configuración de DB** (settings.py)
3. ✅ **Agregar PostgreSQL addon** en Railway
4. ✅ **Configurar variables de entorno**
5. ✅ **Hacer commit y push**

**Tiempo estimado:** 10-15 minutos

¿Necesitas ayuda con algún paso específico?
