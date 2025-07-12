"""
Azure production settings for gestor_vehiculos project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
ALLOWED_HOSTS = [
    '.azurewebsites.net',
    'localhost',
    '127.0.0.1',
]

# Parse additional allowed hosts
additional_hosts = os.environ.get('ALLOWED_HOSTS', '')
if additional_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts.split(',') if host.strip()])

# CORS Configuration
CORS_ALLOWED_ORIGINS = []
cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if cors_origins and cors_origins != '*':
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
    CORS_ALLOW_ALL_ORIGINS = False
else:
    CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https?://\d+\.\d+\.\d+\.\d+:8000$",
]

# Application definition
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
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestor_vehiculos.wsgi.application'

# REST Framework Configuration
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
    'PAGE_SIZE': 10
}

# Database Configuration - SQL Server
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Parse SQL Server URL format: mssql://user:password@host:port/dbname
    import re
    match = re.match(r'mssql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', DATABASE_URL)
    if match:
        user, password, host, port, dbname = match.groups()
        # Remove URL encoding from user (e.g., %40 -> @)
        user = user.replace('%40', '@')
        
        DATABASES = {
            'default': {
                'ENGINE': 'mssql',
                'NAME': dbname.split('?')[0],  # Remove query parameters from dbname
                'USER': user,
                'PASSWORD': password,
                'HOST': host,
                'PORT': port,
                'OPTIONS': {
                    'driver': 'ODBC Driver 18 for SQL Server',
                    'extra_params': 'TrustServerCertificate=yes',
                },
                'CONN_MAX_AGE': 600,
            }
        }
    else:
        # Fallback if URL format is not recognized - use direct configuration for SQL Server
        DATABASES = {
            'default': {
                'ENGINE': 'mssql',
                'NAME': 'ssvq',
                'USER': 'ssvqdb@ssvq',
                'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'ssvq1!flota'),
                'HOST': 'ssvq.database.windows.net',
                'PORT': '1433',
                'OPTIONS': {
                    'driver': 'ODBC Driver 18 for SQL Server',
                    'extra_params': 'TrustServerCertificate=yes',
                },
            }
        }
else:
    # Fallback to original SQL Server configuration
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': 'ssvq',
            'USER': 'ssvqdb@ssvq',
            'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'ssvq1!flota'),
            'HOST': 'ssvq.database.windows.net',
            'PORT': '1433',
            'OPTIONS': {
                'driver': 'ODBC Driver 18 for SQL Server',
                'extra_params': 'TrustServerCertificate=yes',
            },
        }
    }

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'es-cl' 
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True 

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files configuration - Try Azure Blob Storage, fallback to local
try:
    # Only use Azure storage if we have the required environment variables
    AZURE_STORAGE_ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
    AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'media')
    
    if AZURE_STORAGE_ACCOUNT_NAME:
        DEFAULT_FILE_STORAGE = 'asignaciones.storage.AzureBlobStorage'
    else:
        # Fallback to local storage
        DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
except ImportError:
    # If Azure libraries are not available, use local storage
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Application Insights
APPINSIGHTS_CONNECTION_STRING = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
if APPINSIGHTS_CONNECTION_STRING:
    INSTALLED_APPS.append('applicationinsights.django')
    APPLICATION_INSIGHTS = {
        'connection_string': APPINSIGHTS_CONNECTION_STRING,
    }

# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'asignaciones': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
