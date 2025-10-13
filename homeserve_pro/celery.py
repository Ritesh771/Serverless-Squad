""" Celery configuration for HomeServe Pro
Note: Tasks run synchronously in development (no Redis/broker needed)
For production, consider using RabbitMQ or database broker
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserve_pro.settings')

app = Celery('homeserve_pro')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configuration for synchronous task execution (no broker)
app.conf.update(
    task_always_eager=True,  # Execute tasks synchronously
    task_eager_propagates=True,  # Propagate exceptions
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')