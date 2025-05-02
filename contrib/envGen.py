#!/usr/bin/env python

"""
Django SECRET_KEY generator.
"""

from django.utils.crypto import get_random_string

chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"

CONFIG_STRING = """
DEBUG=True
SECRET_KEY=%s
ALLOWED_HOSTS=127.0.0.1, localhost
#Databases (Add your access to database )
DB_ENGINE=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

""".strip() % get_random_string(
    50, chars
)

# Writing our configuration file to '.env'
with open(".env", "w") as configfile:
    configfile.write(CONFIG_STRING)
