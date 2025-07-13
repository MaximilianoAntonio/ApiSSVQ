#!/usr/bin/env python
"""
Script para migrar de MSSQL a PostgreSQL y corregir el error 500 en Railway.
Ejecutar desde el directorio raíz del proyecto Django.

Uso:
python migrate_to_railway.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(step, message):
    print(f"\n{'='*60}")
    print(f"PASO {step}: {message}")
    print('='*60)

def run_command(command, description=""):
    """Ejecuta un comando y maneja errores."""
    print(f"\n🔄 Ejecutando: {command}")
    if description:
        print(f"   {description}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ Éxito: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False

def backup_current_settings():
    """Crear backup de settings.py actual."""
    settings_path = Path("gestor_vehiculos/settings.py")
    backup_path = Path("gestor_vehiculos/settings_backup.py")
    
    if settings_path.exists():
        shutil.copy(settings_path, backup_path)
        print(f"✅ Backup creado: {backup_path}")
        return True
    else:
        print("❌ No se encontró settings.py")
        return False

def update_requirements():
    """Actualizar requirements.txt."""
    requirements_content = """# Requirements for Railway deployment
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
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    
    print("✅ requirements.txt actualizado")

def update_settings():
    """Actualizar settings.py con configuración de Railway."""
    settings_content = '''"""
Django settings for gestor_vehiculos project optimized for Railway.
"""

import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-)i$w*5mx^2esaf$)+oarmvtbf@)-15q(#3#avi@zbw%bqewr5k')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['*']

IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') is not None

if not DEBUG or IS_RAILWAY:
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_TZ = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.vercel.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

CORS_ALLOWED_ORIGINS = [
    'https://frontflota-ofjx-qu4vu5qi3-maximilianoantonios-projects.vercel.app',
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\\.railway\\.app$",
    r"^https://.*\\.vercel\\.app$",
    r"^http://localhost:\\d+$",
]

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken', 
    'corsheaders',
    'asignaciones',
    'django_filters',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gestor_vehiculos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestor_vehiculos.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Database configuration
if IS_RAILWAY:
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-cl' 
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True 

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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
'''
    
    with open("gestor_vehiculos/settings.py", "w") as f:
        f.write(settings_content)
    
    print("✅ settings.py actualizado")

def create_railway_files():
    """Crear archivos necesarios para Railway."""
    
    # railway.json
    railway_config = """{
  "build": {
    "command": "python manage.py collectstatic --noinput && python manage.py migrate"
  },
  "start": {
    "command": "gunicorn gestor_vehiculos.wsgi:application --bind 0.0.0.0:$PORT"
  }
}"""
    
    with open("railway.json", "w") as f:
        f.write(railway_config)
    
    # Procfile (alternativo)
    procfile_content = "web: gunicorn gestor_vehiculos.wsgi:application --bind 0.0.0.0:$PORT"
    with open("Procfile", "w") as f:
        f.write(procfile_content)
    
    print("✅ Archivos de Railway creados")

def main():
    print("🚀 MIGRACIÓN A RAILWAY - CORRECCIÓN ERROR 500")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("manage.py").exists():
        print("❌ Error: No se encontró manage.py. Ejecuta este script desde el directorio raíz del proyecto Django.")
        sys.exit(1)
    
    print_step(1, "Crear backup de configuración actual")
    if not backup_current_settings():
        print("⚠️  Advertencia: No se pudo crear backup")
    
    print_step(2, "Actualizar requirements.txt")
    update_requirements()
    
    print_step(3, "Actualizar settings.py")
    update_settings()
    
    print_step(4, "Crear archivos de configuración de Railway")
    create_railway_files()
    
    print_step(5, "Verificar configuración")
    if run_command("python manage.py check", "Verificando configuración de Django"):
        print("✅ Configuración válida")
    else:
        print("❌ Hay errores en la configuración")
    
    print("\n" + "="*60)
    print("🎉 MIGRACIÓN COMPLETADA")
    print("="*60)
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. En Railway Dashboard:")
    print("   - Agregar PostgreSQL addon")
    print("   - Configurar variables de entorno:")
    print("     * DEBUG=False")
    print("     * SECRET_KEY=tu-clave-secreta-segura")
    print("     * RAILWAY_ENVIRONMENT=production")
    
    print("\n2. Hacer commit y push:")
    print("   git add .")
    print("   git commit -m 'Fix Railway deployment - migrate to PostgreSQL'")
    print("   git push origin main")
    
    print("\n3. Después del deployment:")
    print("   - Ejecutar migraciones (automático con railway.json)")
    print("   - Crear superuser: python manage.py createsuperuser")
    
    print("\n4. Si necesitas migrar datos de MSSQL:")
    print("   - Hacer backup: python manage.py dumpdata > data.json")
    print("   - Cargar en nueva DB: python manage.py loaddata data.json")
    
    print("\n⚠️  IMPORTANTE:")
    print("- El archivo settings_backup.py contiene tu configuración anterior")
    print("- Los archivos originales de MSSQL están en el backup")

if __name__ == "__main__":
    main()
