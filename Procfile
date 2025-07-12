web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn gestor_vehiculos.wsgi --bind 0.0.0.0:$PORT
release: python deploy.py
