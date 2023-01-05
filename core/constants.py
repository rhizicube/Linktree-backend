from core.settings import settings

from celery.task.control import inspect

# Check if celery is working
def is_celery_working():
    insp = inspect()
    status = insp.stats()
    return bool(status)
