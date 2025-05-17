import os
from datetime import timedelta
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


app = Celery('stock-control')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'some_task': {
        'task': 'apps.debts.tasks.deduct_due_debts',
        'schedule': timedelta(seconds=15), 
    }
}