from pydantic import BaseSettings
import os
from kombu import Queue
from celery.schedules import crontab


class Settings(BaseSettings):
	# PostgreSQL connection
	POSTGRE_DB_ENGINE: str = "postgresql"
	POSTGRE_DB_USER: str = "admin@rhizicube.ai"
	POSTGRE_DB_PASS: str = "1234"
	POSTGRE_DB_HOST: str = "localhost"
	POSTGRE_DB_NAME: str = "linktree_db"
	POSTGRE_DB_PORT: int = 5432

	# MongoDB connection
	MONGO_DB_ENGINE: str = "mongodb"
	MONGO_DB_USER: str = "admin@rhizicube.ai"
	MONGO_DB_PASS: str = "1234"
	MONGO_DB_HOST: str = "localhost"
	MONGO_DB_NAME: str = "linktree_db"
	MONGO_DB_PORT: int = 27017

	# Base directory
	BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	# Static and media URLs
	STATIC_URL: str = '/static/'
	MEDIA_URL: str = '/media/'
	STATIC_ROOT: str = os.path.join(BASE_DIR, 'static/')
	MEDIA_ROOT: str = os.path.join(BASE_DIR, 'media/')

	# Path to file containing location details based on IP
	IPv4_LOCATION_FILE_PATH: str = os.path.join(BASE_DIR, 'ip2_locations', "IP2LOCATION-LITE-DB5.BIN")
	IPv6_LOCATION_FILE_PATH: str = os.path.join(BASE_DIR, 'ip2_locations', "IP2LOCATION-LITE-DB9.IPV6.BIN")

	# Celery setup
	AMQP_USER: str = "rhizicube-admin"
	AMQP_PASS: str = "cube123"
	AMQP_HOST: str = "localhost"
	AMQP_PORT: int = 5672
	CELERY_TIMEZONE: str = "UTC"
	def route_task(name, args, kwargs, options, task=None, **kw):
		if ":" in name:
			queue, _ = name.split(":")
			return {"queue": queue}
		return {"queue": "celery"}

	CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", f"amqp://{AMQP_USER}:{AMQP_PASS}@{AMQP_HOST}:{AMQP_PORT}//")
	CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")

	CELERY_TASK_QUEUES: list = (
		# default queue
		Queue("celery"),
		# custom queue
		Queue("trials"),
		Queue("clicks"),
		Queue("views"),
	)

	CELERY_TASK_ROUTES = (route_task,)
	CELERY_BEAT_SCHEDULE = {}

	CELERY_BEAT_SCHEDULE['celery_trial'] = {
		'task': 'tasks.clicks.celery_trials',
		'schedule': crontab(
			minute="*/1", 
			hour="*",
			day_of_month="*",
			month_of_year="*"
			),
	}

settings = Settings()
print(settings.CELERY_BEAT_SCHEDULE)
