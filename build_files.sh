#!/bin/bash

# Install project dependencies
pip install -r requirements.txt

# Make migrations and migrate
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput