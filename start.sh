#!/bin/bash

# Install Microsoft ODBC Driver if not present
if ! dpkg -l | grep -q msodbcsql18; then
    echo "Installing Microsoft ODBC Driver..."
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
    apt-get update
    ACCEPT_EULA=Y apt-get install -y msodbcsql18
fi

# Run Django migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start the application
exec gunicorn --bind 0.0.0.0:$PORT gestor_vehiculos.wsgi:application
