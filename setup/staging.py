"""
Production settings for the project - Vercel + NeonDB
"""
import os
import sys
import dj_database_url
from .settings import *
from decouple import config

# DEBUG deve estar False em produção
DEBUG = False

# =====================================================
# SECURITY SETTINGS
# =====================================================
SECRET_KEY = config('SECRET_KEY', default='')

if not SECRET_KEY:
    # Em produção, SECRET_KEY DEVE ser definida
    raise ValueError(
        "❌ ERRO CRÍTICO: SECRET_KEY não foi definida nas variáveis de ambiente do Vercel!\n"
        "Adicione a variável 'SECRET_KEY' em Settings > Environment Variables no Vercel\n"
        "Você pode gerar uma em: https://djecrety.ir/"
    )

ALLOWED_HOSTS = ["*"]

# =====================================================
# DATABASE CONFIGURATION
# =====================================================
# O dj_database_url parseia a CONNECTION STRING do NeonDB
# Formato esperado: postgresql://user:password@host:port/database?sslmode=require

DATABASE_URL = config('DATABASE_URL', default='').strip()

if DATABASE_URL:
    try:
        # Parse a URL e configure o Django
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                ssl_require=True,
                conn_health_checks=True,
            )
        }
    except ValueError as e:
        raise ValueError(
            f"❌ DATABASE_URL inválida!\n"
            f"Erro: {str(e)}\n"
            f"Certifique-se de que a URL começa com 'postgresql://'\n"
            f"Não use 'psql://' ou 'psql' no início"
        )
else:
    raise ValueError(
        "❌ DATABASE_URL não foi configurada!\n"
        "Adicione em Settings > Environment Variables no Vercel\n"
        "Obtenha a URL no seu dashboard do NeonDB\n"
        "Formato: postgresql://user:password@host:port/database?sslmode=require"
    )

# =====================================================
# STATIC FILES CONFIGURATION
# =====================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise serves static files in production
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =====================================================
# HTTPS/SECURITY SETTINGS
# =====================================================
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# =====================================================
# LOGGING
# =====================================================
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
