#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --no-input
