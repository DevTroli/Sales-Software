#!/bin/bash

echo "Building the project..."
python3.11 -m pip install -r requirements.txt
python3.11 manage.py collectstatic --noinput --clear
echo "Build finished."
