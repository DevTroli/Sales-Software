"""
Production settings for the project.
Corrige o problema de parsing de DATABASE_URL vazia
"""
import os
import sys
import dj_database_url
from .settings import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY
SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key-for-build')
ALLOWED_HOSTS = ["*"]

# =====================================================
# DATABASE CONFIGURATION - CORRIGIDO
# =====================================================
# O erro acontecia porque dj_database_url.config() tentava parsear
# uma string vazia quando DATABASE_URL não era fornecida ou era inválida

DATABASE_URL = config('DATABASE_URL', default='').strip()

if DATABASE_URL:
    try:
        # Valida que a URL começa com um esquema reconhecido
        valid_schemes = ('postgresql://', 'postgres://', 'mysql://', 'sqlite://')
        if not any(DATABASE_URL.startswith(scheme) for scheme in valid_schemes):
            raise ValueError(
                f"URL do banco inválida. Deve começar com um dos esquemas: {valid_schemes}. "
                f"Você forneceu: {DATABASE_URL[:50]}..."
            )
        
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                ssl_require=True,
                conn_health_checks=True,
            )
        }
        print("✅ Banco de dados conectado via DATABASE_URL", file=sys.stderr)
        
    except ValueError as e:
        print(
            f"❌ ERRO: DATABASE_URL inválida. {str(e)}\n"
            f"Usando configuração padrão do settings.py",
            file=sys.stderr
        )
        # Mantém a configuração padrão do settings.py (já foi importada acima)
else:
    print(
        "⚠️  DATABASE_URL não foi configurada nas variáveis de ambiente.\n"
        "Usando configuração padrão do settings.py",
        file=sys.stderr
    )
    # A configuração padrão já foi carregada via: from .settings import *

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise configuration
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# HTTPS settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Log all to console (for Vercel)
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
