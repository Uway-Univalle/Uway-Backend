import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uway_backend.settings')
app = Celery("uway_backend")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()