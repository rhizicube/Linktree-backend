from pydantic import BaseSettings
import os
from celery.schedules import crontab
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".backend.env"))
load_dotenv(dotenv_path=dotenv_path)


def get_celery_beat_scheduled_tasks():
	scheduled_tasks = {}
	
	if os.getenv('ENABLE_TRIAL', "No") == "Yes":
		scheduled_tasks['celery_trial'] = {
			# 'task': 'tasks.clicks.celery_trials',
			'task': 'tasks.visitor_trend.celery_trials_trend',
			'schedule': crontab(
				minute="*/1", 
				hour="*",
				day_of_month="*",
				month_of_year="*"
				),
		}
	if os.getenv('ENABLE_VISITOR_TREND', "No") == "Yes":
		scheduled_tasks['visitor_view_click_trend'] = {
			'task': 'tasks.visitor_trend.save_visitor_sampled_data',
			'schedule': crontab(
				minute="*/2", 
				hour="*",
				day_of_month="*",
				month_of_year="*"
				),
		}
	
	return scheduled_tasks


class Settings(BaseSettings):
	# PostgreSQL connection
	POSTGRE_DB_ENGINE: str = os.environ.get("POSTGRES_ENGINE", "postgresql")
	POSTGRE_DB_USER: str = os.environ.get("POSTGRES_USER", "admin@rhizicube.ai")
	POSTGRE_DB_PASS: str = os.environ.get("POSTGRES_PASSWORD", "1234")
	POSTGRE_DB_HOST: str = os.environ.get("POSTGRES_HOST", "localhost")
	POSTGRE_DB_NAME: str = os.environ.get("POSTGRES_DB", "linktreedb")
	POSTGRE_DB_PORT: int = int(os.environ.get("POSTGRES_PORT", "5432"))

	# MongoDB connection
	MONGO_DB_ENGINE: str = os.environ.get("MONGO_INITDB_ROOT_ENGINE", "mongodb")
	MONGO_DB_USER: str = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "admin@rhizicube.ai")
	MONGO_DB_PASS: str = os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "1234")
	MONGO_DB_HOST: str = os.environ.get("MONGO_INITDB_ROOT_HOST", "localhost")
	MONGO_DB_NAME: str = os.environ.get("MONGO_INITDB_DATABASE", "rhizicubedb")
	MONGO_DB_PORT: int = int(os.environ.get("MONGO_INITDB_ROOT_PORT", "27017"))

	# Base directory
	BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	# Static and media URLs
	STATIC_URL: str = '/static/'
	MEDIA_URL: str = '/media/'
	STATIC_ROOT: str = os.path.join(BASE_DIR, 'static/')
	MEDIA_ROOT: str = os.path.join(BASE_DIR, 'media/')

	# Path to file containing location details based on IP
	# IPv4_LOCATION_FILE_PATH: str = os.path.join(BASE_DIR, 'ip2_locations', "IP2LOCATION-LITE-DB5.BIN")
	# IPv6_LOCATION_FILE_PATH: str = os.path.join(BASE_DIR, 'ip2_locations', "IP2LOCATION-LITE-DB9.IPV6.BIN")

	# Celery setup
	AMQP_USER: str = "rhizicube-admin"
	AMQP_PASS: str = "cube123"
	AMQP_HOST: str = "localhost"
	AMQP_PORT: int = 5672
	CELERY_TIMEZONE: str = "UTC"
	CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", f"amqp://{AMQP_USER}:{AMQP_PASS}@{AMQP_HOST}:{AMQP_PORT}//")
	CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")
	CELERY_BEAT_SCHEDULE = get_celery_beat_scheduled_tasks()

	

settings = Settings()
# print(settings.CELERY_BEAT_SCHEDULE)
