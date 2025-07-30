#!/usr/bin/env bash
# Build script for Render.com

echo "🚀 Building kho my pham application..."

# Install dependencies
pip install -r requirements_production.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

echo "✅ Build completed!" 