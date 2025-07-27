python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py seed_system_admin
uvicorn uway_backend.asgi:application --host 0.0.0.0 --port 8000 --reload