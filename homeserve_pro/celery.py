"""
Celery configuration for HomeServe Pro
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

# Optional configuration, see the application user guide.
app.conf.update(
    task_track_started=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_backend='redis://localhost:6379/0',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'core.tasks.generate_pincode_analytics': {'queue': 'analytics'},
        'core.tasks.send_pincode_demand_alerts': {'queue': 'notifications'},
        'core.tasks.send_vendor_bonus_alerts': {'queue': 'notifications'},
        'core.tasks.send_promotional_campaigns': {'queue': 'notifications'},
        'core.tasks.check_pending_signatures': {'queue': 'monitoring'},
        'core.tasks.check_payment_holds': {'queue': 'monitoring'},
        'core.tasks.check_booking_timeouts': {'queue': 'monitoring'},
        'core.tasks.send_vendor_completion_reminders': {'queue': 'notifications'},
        'core.tasks.cleanup_old_notifications': {'queue': 'maintenance'},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Beat configuration
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')