from celery import shared_task, current_app
from core.settings import settings
from datetime import datetime as dt, timedelta
from crud import profiles, clicks, clicks_resample, views, views_resample, links
from sqlalchemy.orm import session
from db_connect.setup import get_db
from core.constants import is_celery_working
import pandas as pd
import json
from utilities.views import get_ip_location
from asgiref.sync import async_to_sync
from db_connect.setup import connect_to_mongo, close_mongo_connection


celery_app = current_app
celery_app.config_from_object(settings, namespace='CELERY')
celery_app.conf.update(task_track_started=True)
celery_app.conf.update(task_serializer='pickle')
celery_app.conf.update(result_serializer='pickle')
celery_app.conf.update(accept_content=['pickle', 'json'])
celery_app.conf.update(result_expires=200)
celery_app.conf.update(result_persistent=True)
celery_app.conf.update(worker_send_task_events=False)
celery_app.conf.update(worker_prefetch_multiplier=1)



async def query_sample_click(resampled_views, start_time, end_time, db):
	"""Async function to sample clicks for every sampled view for the same date-time range

	Args:
		resampled_views (orm queryset): The inserted resampled views
		start_time (str): Start time
		end_time (str): End time
		db (session): DB connection to PostgreSQL
	"""
	resampled_clicks = []
	for view in resampled_views:
		view_clicks = await clicks.get_clicks_by_session_datetime_range(view["session_id"], start_time, end_time)
		if len(view_clicks) == 0:
			continue
		view_id = views_resample.get_views_by_session(db, view["session_id"]).id
		clicks_df = pd.DataFrame(view_clicks)
		clicks_df['click_created'] = pd.to_datetime(clicks_df['click_created']) # To convert click_created format (string to datetime)
		clicks_df["count"] = 1 # To calculate the total view counts
		# For each unique session, the click counts for each link is calculated with an interval of 1 hour (60 minutes)
		for s in clicks_df["session_id"].unique():
			session_df = clicks_df[clicks_df["session_id"]==s]
			pivoted_data = session_df.pivot_table(index="click_created", values=["count"], columns="link")
			pivoted_data = pivoted_data.resample('60min').sum()
			pivoted_data.columns=pivoted_data.columns.get_level_values(1)
			fieldnames = pivoted_data.columns
			for index, row in pivoted_data.iterrows():
				for l in fieldnames:
					resampled_clicks.append({"click_count": int(row[l]), "click_sampled_timestamp": index.to_pydatetime(), "view_id": view_id, "link_id": links.get_link_by_tiny_url(l, db).id})
	if len(resampled_clicks) > 0:
		# The data analyzed for each hour for each unique session is inserted in bulk to the DB	
		clicks_resample.bulk_create_click(db, resampled_clicks)
		print("Completed inserting clicks")


async def query_sample_view(profile, last_queried):
	"""Async function to sample views for a profile between a particular date-time range

	Args:
		profile (orm queryset): Profile information
		last_queried (dict): Information on the last queried and resampled timestamp
	"""
	# As FastAPI isnt used directly, SQL DB session and MongoDB session needs to be opened/closed separately
	db:session=next(get_db())
	await connect_to_mongo()
	# time ranges between the last timestamp which was queried, to the previous hour
	start_time = last_queried.get("profile_last_queried_timestamp", None)
	end = dt.utcnow()-timedelta(hours=1)
	end_time = dt.strftime(end.replace(minute=59, second=59), "%Y-%m-%dT%H:%M:%S") # Get the very last second of the previous hour
	profile_views = await views.get_views_by_profile_datetime_range(profile.id, None, end_time)
	if len(profile_views) == 0:
		print(f"No views to resample between time {start_time} and {end_time}")
		db.close()
		await close_mongo_connection()
		return
	# Update the last queried timestamp to end_time
	last_queried["profile_last_queried_timestamp"] = end_time
	profiles.update_profile(db, profile.id, desc=last_queried)
	views_df = pd.DataFrame(profile_views)
	views_df["location_ip"] = [x["ip"] for x in views_df["location"]] # To store the IP address separately
	views_df['view_created'] = pd.to_datetime(views_df['view_created']) # To convert view_created format (string to datetime)
	views_df["count"] = 1 # To calculate the total view counts
	resampled_views = []
	# For each unique session, the view counts for each IP address is calculated with an interval of 1 hour (60 minutes)
	for s in views_df["session_id"].unique():
		try:
			st = dt.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
		except Exception as e:
			st = dt.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f")
		session_df = views_df[(views_df["session_id"]==s) & (views_df["view_created"]>st)]
		if session_df.empty:
			continue
		pivoted_data = session_df.pivot_table(index="view_created", values=["count"], columns="location_ip")
		pivoted_data = pivoted_data.resample('60min').sum()
		pivoted_data.columns=pivoted_data.columns.get_level_values(1)
		fieldnames = pivoted_data.columns
		for index, row in pivoted_data.iterrows():
			for ip in fieldnames:
				location = get_ip_location(ip)
				resampled_views.append({"session_id": s, "device_type": session_df.iloc[0]["device"], "view_count": int(row[ip]), "view_location": location, "view_sampled_timestamp": index.to_pydatetime(), "profile": profile.id})
	if len(resampled_views) > 0:
		# The data analyzed for each hour for each unique session is inserted in bulk to the DB
		views_resample.bulk_create_view(db, resampled_views)
	await query_sample_click(profile_views, start_time, end_time, db)
	db.close()
	await close_mongo_connection()


# @shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})#,name='trials:trial')
@celery_app.task(name="analytics:query_sample_view_clicks")
def query_sample_view_clicks(profile, last_queried):
	"""Task to run all the async functionalities for each profile separately

	Args:
		profile (orm queryset): Profile information
		last_queried (dict): Information on the last queried and resampled timestamp
	"""
	async_to_sync(query_sample_view)(profile, last_queried)
	# await query_sample_view(profile, last_queried)


# @shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
@celery_app.task(name="analytics:save_visitor_sampled_data")
def save_visitor_sampled_data():
	"""Scheduled task to sample raw data from clicks and views from MongoDB and store it in PostgreSQL
	"""
	# As FastAPI isnt used directly, SQL DB session needs to be opened/closed separately
	db:session=next(get_db())
	all_profiles = profiles.get_all_profiles(db)
	# Sample views and clicks for each profile separately
	for profile in all_profiles:
		last_queried = profile.profile_description
		if last_queried in ['', "", None, "''"]:
			last_queried = {'profile_last_queried_timestamp': None}
		else:
			last_queried = json.loads(last_queried)
  
		print("profile_last_queried ++", last_queried)
		# Each profile runs as a separate task
		if is_celery_working() == True:
			print("Celery working")
			task = query_sample_view_clicks.delay(profile, last_queried)
		else:
			print("Celery not working")
			query_sample_view_clicks(profile, last_queried)
	db.close()
