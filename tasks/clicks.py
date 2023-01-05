from celery import shared_task
from datetime import datetime as dt


@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})#,name='trials:trial')
def celery_trials(self):
	print("Celery running at :::", dt.now())
