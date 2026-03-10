#!/usr/bin/env bash
# Render build script
set -o errexit

pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Ensure data directory exists for SQLite
mkdir -p /data

# Run database migrations
python manage.py migrate
