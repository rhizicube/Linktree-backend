from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from datetime import datetime as dt
import pandas as pd
from crud import profiles
from utilities.analysis import merge_total_unique_views_clicks, get_views_total_unique, get_clicks_total_unique, get_location_wise_counts
from db_connect.setup import get_db

analytics_router = APIRouter()

@analytics_router.get("/getcountbylink/")
async def get_count_by_link(username:str, start_date:dt=None, end_date:dt=None, db:session=Depends(get_db)):
	"""API to get click counts of all links created by user

	Args:
		username (str): Username
		start_date (dt): start time
		end_date (dt): end time
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		dict: click count for every link created for a user
	"""
	try:
		if start_date is None or end_date is None:
			return JSONResponse(content={"message": "Start and end date range should be provided"}, status_code=status.HTTP_400_BAD_REQUEST)
		# Raw SQL query to get all the links (id only) present for a user
		profile_links = db.execute("SELECT Link.id FROM Link, Profile WHERE Profile.id = Link.profile_id AND Profile.username = :uname;", {"uname": username})
		links = profile_links.mappings().all()
		if len(links) == 0:
			return JSONResponse(content={"message": "Links not created by user"}, status_code=status.HTTP_404_NOT_FOUND)

		# Raw SQL query to get click count and link name for all the clicks recorded in clicksresample table between given date range for only the list of links queried above
		click_count = db.execute('SELECT ClicksResample.click_count, Link.link_name FROM ClicksResample, Link WHERE Link.id = ClicksResample.link_id AND link_id in :link_list AND click_sampled_timestamp BETWEEN :start AND :end;', { 'link_list': tuple(x['id'] for x in links), "start": start_date, "end": end_date })
		click_count = click_count.mappings().all()
		if len(click_count) == 0:
			return JSONResponse(content={"message": "Data not found for the given date range"}, status_code=status.HTTP_404_NOT_FOUND)
		
		click_count_df = pd.DataFrame(click_count)
		# To get the total clicks count for each link
		clicks_grouped_by_link = click_count_df.groupby([click_count_df.link_name])["click_count"].sum()
		# TODO: To try sorting by counts in descending order
		# clicks_grouped_by_link.sort_values('click_count', ascending=False, inplace=True)
		print(clicks_grouped_by_link)
		# Response formatting
		clicks_response_data = {}
		for index, row in clicks_grouped_by_link.items():
			clicks_response_data[index] = row
		return JSONResponse(content={"data": clicks_response_data}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@analytics_router.get("/getactivitycountbyfrequency/")
async def get_activity_by_frequency(username: str, start_date: dt, end_date: dt, db:session=Depends(get_db)):
	"""API to get activity count for daily, weekly and monthly frequencies

	Args:
		username (str): username
		start (dt): start time
		end (dt): end time
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: views, clicks and CTR count between given date range for a user's profile segregated based on daily, weekly and monthly
	"""
	try:
		# Initial checks for input parameters
		if not start_date or not end_date or end_date < start_date:
			return JSONResponse(content={"message": "Valid start and end dates are required"}, status_code=status.HTTP_400_BAD_REQUEST)
		usernames = profiles.get_all_usernames(db)
		if username not in usernames:
			return JSONResponse(content={"message": f"Profile for user {username} not found"}, status_code=status.HTTP_404_NOT_FOUND)

		# Get view count, sampled timestamp and view id for a profile between given time range
		views = db.execute("SELECT view_count, view_sampled_timestamp, ViewsResample.id FROM ViewsResample, Profile WHERE ViewsResample.profile_id = Profile.id AND Profile.username = :uname AND view_sampled_timestamp BETWEEN :start AND :end", {"uname": username, "start": start_date, "end": end_date})
		_views_df = pd.DataFrame(views.fetchall())
		if _views_df.empty:
			return JSONResponse(content={"message": f"No data found for the specified date range"}, status_code=status.HTTP_404_NOT_FOUND)

		# Get total total views and unique views grouped by date
		views_grouped_by_date, views_unique_grouped_by_date = get_views_total_unique(_views_df)
		
		# Get links created for user's profile
		profile_links = db.execute("SELECT Link.id FROM Link, Profile WHERE Profile.id = Link.profile_id AND Profile.username = :uname;", {"uname": username})
		links = profile_links.mappings().all()
		if len(links) == 0:
			print("Links not created by user")
			clicks_grouped_by_date = pd.DataFrame()
			clicks_unique_grouped_by_date_view = pd.DataFrame()
		else:
			# Raw SQL query to get click count and link id, sampled timestamp and corresponding view id for all the clicks recorded in clicksresample table between given date range for only the list of links queried above
			click_count = db.execute('SELECT ClicksResample.click_count, ClicksResample.link_id, ClicksResample.click_sampled_timestamp, ClicksResample.view_id FROM ClicksResample, Link WHERE Link.id = ClicksResample.link_id AND link_id in :link_list AND click_sampled_timestamp BETWEEN :start AND :end;', { 'link_list': tuple(x['id'] for x in links), "start": start_date, "end": end_date })
			click_count = click_count.mappings().all()
			
			_clicks_df = pd.DataFrame(click_count)
			if _clicks_df.empty:
				print("Clicks not present for profile's links")
				clicks_grouped_by_date = pd.DataFrame()
				clicks_unique_grouped_by_date_view = pd.DataFrame()
			else:
				# Get total total clicks and unique clicks grouped by date
				clicks_grouped_by_date, clicks_unique_grouped_by_date_view = get_clicks_total_unique(_clicks_df)

		# To get daily, weekly and monthly sampled view counts, click counts and CTR
		view_click_group_merge = merge_total_unique_views_clicks(views_grouped_by_date, clicks_grouped_by_date, views_unique_grouped_by_date, clicks_unique_grouped_by_date_view)
		
		print(view_click_group_merge)
		return JSONResponse(content={"data": view_click_group_merge}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@analytics_router.get("/getactivitycount/")
async def get_activity(username:str, db:session=Depends(get_db)):
	"""API to get a user's entire views, clicks and CTR

	Args:
		username (str): username
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Total count of views, clicks and CTR for a user's profile
	"""
	# get the total views and clicks for the profile with username
	try:
		usernames = profiles.get_all_usernames(db)
		if username not in usernames:
			return JSONResponse(content={"message": f"User with username {username} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		# total views for the profile
		views = db.execute("SELECT SUM(view_count) FROM ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username", {"username": username})
		total_views = views.fetchone()[0]
		if total_views == None:
			total_views = 0
		# total clicks for the profile
		clicks = db.execute("SELECT SUM(click_count) FROM ClicksResample, ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND ViewsResample.id = ClicksResample.view_id", {"username": username})
		total_clicks = clicks.fetchone()[0]
		if total_clicks == None:
			total_clicks = 0
		# ctr = total_clicks/total_views
		ctr=0
		if total_views != 0 and total_clicks != 0:
			ctr = round(total_clicks/total_views*100, 3)
		return JSONResponse(content={"data": {"views": total_views, "clicks": total_clicks, "ctr": ctr}}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@analytics_router.get("/getcountbydevice/")
async def get_devices_percentage(username: str, start_date: dt, end_date: dt, db:session=Depends(get_db)):
	"""API to get profile's device activity in percentage

	Args:
		username (str): Username
		start_date (dt): start time
		end_date (dt): end time
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: percentage of usage of each device type
	"""
	try:
		if start_date is None or end_date is None or end_date < start_date:
			return JSONResponse(content={"message": "Valid start and end date ranges should be provided"}, status_code=status.HTTP_400_BAD_REQUEST)

		# Get view count of each device type present for views under the given user's profile
		views_count = db.execute("SELECT ViewsResample.device_type, SUM(ViewsResample.view_count) FROM ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :uname AND view_sampled_timestamp BETWEEN :start AND :end GROUP BY ViewsResample.device_type;", {"uname": username, "start": start_date, "end": end_date})
		views_count = views_count.mappings().all()
		if len(views_count) == 0:
			return JSONResponse(content={"message": "Data not found for the given date range"}, status_code=status.HTTP_404_NOT_FOUND)

		views_df = pd.DataFrame(views_count)
		# Calculate device activity Percentage
		views_df['percent'] = round((views_df['sum'] / views_df['sum'].sum()) * 100, 3)
		# Formatting response
		response_data = {row["device_type"]: row["percent"] for _, row in views_df.iterrows()}
		return JSONResponse(content={"data": response_data}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@analytics_router.get("/getcountbylocation/")
async def get_location_activity(username: str, start_date: dt, end_date: dt, db:session=Depends(get_db)):
	"""API to get profile's location activity in percentage

	Args:
		username (str): Username
		start_date (dt): start time
		end_date (dt): end time
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: percentage of usage country wise, region wise and city wise
	"""
	try:
		if start_date is None or end_date is None or end_date < start_date:
			return JSONResponse(content={"message": "Valid start and end date ranges should be provided"}, status_code=status.HTTP_400_BAD_REQUEST)

		# Get view count of each location present for views under the given user's profile
		views_count = db.execute("SELECT ViewsResample.view_location, ViewsResample.view_count, ViewsResample.id FROM ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :uname AND view_sampled_timestamp BETWEEN :start AND :end;", {"uname": username, "start": start_date, "end": end_date}).fetchall()
		if len(views_count) == 0:
			return JSONResponse(content={"message": "Data not found for the given date range"}, status_code=status.HTTP_404_NOT_FOUND)
		views_count = [x._asdict() for x in views_count] # To convert sqlalchemy.engine.row.RowMapping to dictionary (to access view_location easily)

		views_df = pd.DataFrame(views_count)
		# Get country, region and city wise views count
		views_data = get_location_wise_counts(views_df, "view_count")

		# Get click count of each location present for views under the given user's profile
		print(tuple(x['id'] for x in views_count))
		clicks_count = db.execute("SELECT ViewsResample.view_location, ClicksResample.click_count FROM ViewsResample, ClicksResample WHERE ClicksResample.view_id IN :view_list AND click_sampled_timestamp BETWEEN :start AND :end;", {"view_list": tuple(x['id'] for x in views_count), "start": start_date, "end": end_date}).fetchall()
		if len(clicks_count) == 0:
			print("Clicks not found for the given date range")
			clicks_data = {"country": {}, "region": {}, "city": {}}
		else:
			views_count = [x._asdict() for x in clicks_count] # To convert sqlalchemy.engine.row.RowMapping to dictionary (to access view_location easily)

			clicks_df = pd.DataFrame(clicks_count)
			# Get country, region and city wise clicks count
			clicks_data = get_location_wise_counts(clicks_df, "click_count")

		# Get formatted response
		response_data = {"views": views_data, "clicks": clicks_data}
		return JSONResponse(content={"data": response_data}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@analytics_router.get("/getcountbysocialicon/")
async def get_count_by_profile_social(username:str, start_date:dt=None, end_date:dt=None, db:session=Depends(get_db)):
	"""API to get click counts of all links created by user

	Args:
		username (str): Username
		start_date (dt): start time
		end_date (dt): end time
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		dict: click count for every link created for a user
	"""
	try:
		if start_date is None or end_date is None:
			return JSONResponse(content={"message": "Start and end date range should be provided"}, status_code=status.HTTP_400_BAD_REQUEST)
		# Raw SQL query to get all the links (id only) present for a user
		profile_links = db.execute("SELECT Link.id FROM Link, Profile, Setting WHERE Profile.id = Setting.profile_id AND Link.setting_id = Setting.id AND Profile.username = :uname;", {"uname": username})
		links = profile_links.mappings().all()
		if len(links) == 0:
			return JSONResponse(content={"message": "Links not created by user"}, status_code=status.HTTP_404_NOT_FOUND)

		# Raw SQL query to get click count and link name for all the clicks recorded in clicksresample table between given date range for only the list of links queried above
		click_count = db.execute('SELECT ClicksResample.click_count, Link.link_name FROM ClicksResample, Link WHERE Link.id = ClicksResample.link_id AND link_id in :link_list AND click_sampled_timestamp BETWEEN :start AND :end;', { 'link_list': tuple(x['id'] for x in links), "start": start_date, "end": end_date })
		click_count = click_count.mappings().all()
		if len(click_count) == 0:
			return JSONResponse(content={"message": "Data not found for the given date range"}, status_code=status.HTTP_404_NOT_FOUND)
		
		click_count_df = pd.DataFrame(click_count)
		# To get the total clicks count for each link
		clicks_grouped_by_link = click_count_df.groupby([click_count_df.link_name])["click_count"].sum()
		# TODO: To try sorting by counts in descending order
		# clicks_grouped_by_link.sort_values('click_count', ascending=False, inplace=True)
		print(clicks_grouped_by_link)
		# Response formatting
		clicks_response_data = {}
		for index, row in clicks_grouped_by_link.items():
			clicks_response_data[index] = row
		return JSONResponse(content={"data": clicks_response_data}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
