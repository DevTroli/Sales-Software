"""
WSGI config for setup project.
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.staging')

# Vercel precisa do handler nomeado como 'app'
django_application = get_wsgi_application()
application = WhiteNoise(django_application)

# Explicita o handler para o Vercel
app = application