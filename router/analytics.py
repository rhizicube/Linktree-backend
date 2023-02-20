from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from datetime import datetime as dt
import pandas as pd
from crud import profiles
import json
from utilities.analysis import get_activity
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
async def get_activity_test(username: str, start_date: dt, end_date: dt, sample_frequency: str, db:session=Depends(get_db)):
	"""API to get User's profile activity by frequency

	Args:
		username (str): Username
		start_date (dt): start time
		end_date (dt): end time
		sample_frequency (str): sample data on a daily/weekly/monthly basis
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: _description_
	"""
	try:
		usernames = profiles.get_all_usernames(db)
		if username not in usernames:
			return JSONResponse(content={"message": f"User with username {username} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		if not start_date or not end_date:
			return JSONResponse(content={"message": "start and end dates are required"}, status_code=status.HTTP_400_BAD_REQUEST)
		if start_date>end_date:
			return JSONResponse(content={"message": "start date should be less than end date"}, status_code=status.HTTP_400_BAD_REQUEST)
		if sample_frequency.lower() not in ["daily", "weekly", "monthly"]:
			return JSONResponse(content={"message": "sample_frequency should be daily, weekly or monthly"}, status_code=status.HTTP_400_BAD_REQUEST)
		
		# Get total and unique views and clicks sampled by daily/weekly/monthly between the given date range
		response_data = get_activity(username, start_date, end_date, sample_frequency.lower(), db)
		response_data = pd.DataFrame(response_data)
		response_data = response_data.groupby("date").sum().reset_index()
		# Get CTR for given date-time in dataframe
		response_data["ctr"] = [0 if row["total_views"]==0 else round(row["total_clicks"]/row["total_views"]*100, 3) for index, row in response_data.iterrows()]
		response_data = response_data.to_dict(orient="records")
		response_data = json.dumps(response_data, default=str)
		response_data = {"data": response_data}
		response_data = json.loads(response_data["data"])
		return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@analytics_router.get("/getactivitycount/")
async def get(username:str, db:session=Depends(get_db)):
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
			ctr = round(total_clicks/total_views, 3)
		return JSONResponse(content={"data": {"views": total_views, "clicks": total_clicks, "ctr": ctr}}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
