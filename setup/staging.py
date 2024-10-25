from .settings import *  # Importa todas as configurações do settings.py

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "railway",  # nome do banco de dados em staging
        "USER": "postgres",  # usuário de staging
        "PASSWORD": "rlXzTQrPrZzlOqbTQXpZKUXxdibZuYDT",  # senha do banco de dados em staging
        "HOST": "autorack.proxy.rlwy.net",  # host do banco de staging
        "PORT": "21844",  # porta do banco de staging
    }
}

# Outras configurações específicas de staging
DEBUG = True
