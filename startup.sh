#!/bin/bash

echo "Starting Django application deployment..."

# Set Python path
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Set Django settings module for Azure
export DJANGO_SETTINGS_MODULE=gestor_vehiculos.settings_azure

# Install dependencies if requirements.txt exists
if [ -f "/home/site/wwwroot/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    python -m pip install --upgrade pip
    pip install -r /home/site/wwwroot/requirements.txt
fi

# Change to the application directory
cd /home/site/wwwroot

echo "Django settings module: $DJANGO_SETTINGS_MODULE"

# Check if we can import Django
python -c "import django; print(f'Django version: {django.get_version()}')"

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --noinput --settings=gestor_vehiculos.settings_azure

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=gestor_vehiculos.settings_azure

# Check Django configuration
echo "Checking Django configuration..."
python manage.py check --settings=gestor_vehiculos.settings_azure

echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout 600 --access-logfile=- --error-logfile=- gestor_vehiculos.wsgi:application
