#!/usr/bin/env bash
# Render build script
set -o errexit

# Create venv and install dependencies
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# Collect static files
./venv/bin/python manage.py collectstatic --no-input
