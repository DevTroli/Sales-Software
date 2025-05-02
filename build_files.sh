#!/bin/bash

# Garante que estamos usando a versão correta
/usr/local/bin/python3.11 -m pip install --upgrade pip
/usr/local/bin/python3.11 -m pip install -r requirements.txt

# Comandos Django
/usr/local/bin/python3.11 manage.py makemigrations
/usr/local/bin/python3.11 manage.py migrate
/usr/local/bin/python3.11 manage.py collectstatic --noinput