#!/usr/bin/env bash
# Render build script
set -o errexit

python3 -m pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --no-input
