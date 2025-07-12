#!/bin/bash

echo "Starting Django application deployment..."

# Set Python path
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Install dependencies if requirements.txt exists
if [ -f "/home/site/wwwroot/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r /home/site/wwwroot/requirements.txt
fi

# Set Django settings module for Azure
export DJANGO_SETTINGS_MODULE=gestor_vehiculos.settings_azure

# Change to the application directory
cd /home/site/wwwroot

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
# echo "Creating superuser..."
# python manage.py shell -c "
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
#     print('Superuser created successfully')
# else:
#     print('Superuser already exists')
# "

echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout 600 gestor_vehiculos.wsgi:application
