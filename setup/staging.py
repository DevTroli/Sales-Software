"""
Django settings for production (Vercel + NeonDB)
"""
import os
import sys
from .settings import *
from decouple import config
import dj_database_url

DEBUG = False

SECRET_KEY = config('SECRET_KEY', default='')
if not SECRET_KEY:
    raise ValueError("❌ ERRO: Defina a variável de ambiente SECRET_KEY no Vercel")

ALLOWED_HOSTS = ["*"]

# DATABASE CONFIGURATION
DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
        conn_health_checks=True,
    )
else:
    import warnings
    warnings.warn("⚠️  DATABASE_URL não configurada!")

# STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MIDDLEWARE = [m for m in MIDDLEWARE if m != 'whitenoise.middleware.WhiteNoiseMiddleware']
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# SECURITY
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
