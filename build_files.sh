#!/bin/bash

# Garante que estamos usando a versão correta
/usr/local/bin/python3.11 -m pip install --upgrade pip
/usr/local/bin/python3.11 -m pip install -r requirements.txt

# Comandos Django
/usr/local/bin/python3.11 manage.py makemigrations
/usr/local/bin/python3.11 manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | /usr/local/bin/python3.11 manage.py shell
/usr/local/bin/python3.11 manage.py collectstatic --noinput