from fastapi import Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from db_connect.setup import get_db
from datetime import datetime as dt
from crud import profiles
import pandas as pd
import json


# view_resample: session_id, view_count, timestamp for profiles
# clicks_resample: link_id,  click_count, timestamp for all links in profile
# convert timestamp to datetime
# view_count: groupby daily, weekly, monthly
# click_count: groupby daily, weekly, monthly
# unique_views: diff session_id
# unique_clicks: diff link_id for unique views_id
# concat total_views, total_clicks, unique_views, unique_clicks
# rename cols in pandas
# ctr
# create separate col date 
# convert to dict
# return dict
# write a function get_activity() to perform the above steps

def get_activity(username: str, start: dt, end: dt, freq: str, db : session = get_db()):
	"""Function to get a user's total/unique views/clicks between a date range

	Args:
		username (str): Username
		start (dt): start time
		end (dt): end time
		freq (str): sampling frequency
		db (session, optional): DB connection session for db functionalities. Defaults to get_db().

	Returns:
		dataframe: Data on count of total/unique clicks/views
	"""
	try:
		profile = profiles.get_profile_by_user(db, username)
		profile_id = profile.id
		views = db.execute("SELECT id, session_id, view_count, view_sampled_timestamp FROM ViewsResample WHERE ViewsResample.profile_id = :profile_id AND view_sampled_timestamp BETWEEN :start AND :end", {"profile_id": profile_id, "start": start, "end": end})
		_views_df = pd.DataFrame(views.fetchall())
		if _views_df.empty:
			return JSONResponse(content={"message": f"No data found for the specified date range"}, status_code=status.HTTP_404_NOT_FOUND)
		_views_df["view_sampled_timestamp"] = pd.to_datetime(_views_df["view_sampled_timestamp"])
		_views_df = _views_df.set_index("view_sampled_timestamp")
		# print(_views_df)
		if freq == "daily":
			views_grouped_by_date = _views_df.groupby(_views_df.index.date)["view_count"].sum()
		elif freq == "weekly":
			year = dt.now().strftime("%Y")
			views_grouped_by_date = _views_df.groupby(_views_df.index.week)["view_count"].sum()
			views_grouped_by_date.index = views_grouped_by_date.index.map(lambda x: dt.strptime(f"{year}-{x}-1", "%Y-%W-%w"))
		elif freq == "monthly":
			year = dt.now().strftime("%Y")
			views_grouped_by_date = _views_df.groupby(_views_df.index.month)["view_count"].sum()
			views_grouped_by_date.index = views_grouped_by_date.index.map(lambda x: dt.strptime(f"{year}-{x}-1", "%Y-%m-%d"))
		else:
			return JSONResponse(content={"message": f"Invalid frequency"}, status_code=status.HTTP_400_BAD_REQUEST)
		views_grouped_by_date = views_grouped_by_date.reset_index()
		# rename index to date
		views_grouped_by_date = views_grouped_by_date.rename(columns={"index": "date", "view_count": "total_views", "view_sampled_timestamp": "date"})
		print(views_grouped_by_date)
		# get unique views
		if freq == "daily":
			unique_views_grouped_by_date = _views_df.groupby(_views_df.index.date)["session_id"].nunique()
		elif freq == "weekly":
			year = dt.now().strftime("%Y")
			unique_views_grouped_by_date = _views_df.groupby(_views_df.index.week)["session_id"].nunique()
			unique_views_grouped_by_date.index = unique_views_grouped_by_date.index.map(lambda x: dt.strptime(f"{year}-{x}-1", "%Y-%W-%w"))
		elif freq == "monthly":
			year = dt.now().strftime("%Y")
			unique_views_grouped_by_date = _views_df.groupby(_views_df.index.month)["session_id"].nunique()
			unique_views_grouped_by_date.index = unique_views_grouped_by_date.index.map(lambda x: dt.strptime(f"{year}-{x}-1", "%Y-%m-%d"))
		else:
			return JSONResponse(content={"message": f"Invalid frequency"}, status_code=status.HTTP_400_BAD_REQUEST)
		unique_views_grouped_by_date = unique_views_grouped_by_date.reset_index()
		# rename session_id to unique_views
		unique_views_grouped_by_date = unique_views_grouped_by_date.rename(columns={"session_id": "unique_views", "index": "date", "view_sampled_timestamp": "date"})
		print(unique_views_grouped_by_date)

		# get clicks
		view_ids = list(_views_df["id"])
		clicks = db.execute("SELECT click_count, link_id, click_sampled_timestamp, view_id FROM ClicksResample, ViewsResample WHERE ViewsResample.id = ClicksResample.view_id AND view_id in :views_list AND click_sampled_timestamp BETWEEN :start AND :end", {"views_list": tuple(view_ids), "start": start, "end": end})
		_clicks_df = pd.DataFrame(clicks.fetchall())
		if _clicks_df.empty:
			return JSONResponse(content={"message": f"No data found for the specified date range"}, status_code=status.HTTP_404_NOT_FOUND)
		_clicks_df["click_sampled_timestamp"] = pd.to_datetime(_clicks_df["click_sampled_timestamp"])
		_clicks_df = _clicks_df.set_index("click_sampled_timestamp")
		if freq == "daily":
			clicks_grouped_by_date = _clicks_df.groupby(_clicks_df.index.date)["click_count"].sum()
		elif freq == "weekly":
			year = dt.now().strftime("%Y")
			clicks_grouped_by_date = _clicks_df.groupby(_clicks_df.index.week)["click_count"].sum()
			clicks_grouped_by_date.index = clicks_grouped_by_date.index.map(lambda x: dt.strptime(f"{year}-{x}-1", "%Y-%W-%w"))
		elif freq == "monthly":
			year = dt.now().strftime("%Y")
			clicks_grouped_by_date = _clicks_df.groupby(_clicks_df.index.month)["click_count"].sum()
			clicks_grouped_by_date.index = clicks_grouped_by_date.index.map(lambda x: dt.strptime(f"{year}-{x}-1", "%Y-%m-%d"))
		else:
			return JSONResponse(content={"message": f"Invalid frequency"}, status_code=status.HTTP_400_BAD_REQUEST)
		clicks_grouped_by_date = clicks_grouped_by_date.reset_index()
		# rename index to date
		clicks_grouped_by_date = clicks_grouped_by_date.rename(columns={"index": "date", "click_count": "total_clicks", "click_sampled_timestamp": "date"})
		print(clicks_grouped_by_date)
		# add new col "temp" to _clicks_df which is a list of tuples of link_id and view_id
		_clicks_df["unique_clicks"] = list(zip(_clicks_df["link_id"], _clicks_df["view_id"])) 
		print(_clicks_df)

		# get unique clicks
		if freq == "daily":
			unique_clicks_grouped_by_date = _clicks_df.groupby(_clicks_df.index.date)["unique_clicks"].nunique()
		elif freq == "weekly":
			year = dt.now().strftime("%Y")
			unique_clicks_grouped_by_date = _clicks_df.groupby(_clicks_df.index.week)["unique_clicks"].nunique()
			unique_clicks_grouped_by_date.index = unique_clicks_grouped_by_date.index.map(lambda x: dt.strptime(f"{year}-{x}-1", "%Y-%W-%w"))
		elif freq == "monthly":
			year = dt.now().strftime("%Y")
			unique_clicks_grouped_by_date = _clicks_df.groupby(_clicks_df.index.month)["unique_clicks"].nunique()
			unique_clicks_grouped_by_date.index = unique_clicks_grouped_by_date.index.map(lambda x: dt.strptime(f"{year}-{x}-1", "%Y-%m-%d"))
		else:
			return JSONResponse(content={"message": f"Invalid frequency"}, status_code=status.HTTP_400_BAD_REQUEST)
		unique_clicks_grouped_by_date = unique_clicks_grouped_by_date.reset_index()
		# # rename session_id to unique_clicks
		unique_clicks_grouped_by_date = unique_clicks_grouped_by_date.rename(columns={"index": "date", "click_sampled_timestamp": "date"})
		print(unique_clicks_grouped_by_date)
		response_data = pd.concat([views_grouped_by_date, unique_views_grouped_by_date])
		response_data = pd.concat([response_data, clicks_grouped_by_date])
		response_data = pd.concat([response_data, unique_clicks_grouped_by_date])
		response_data = response_data.fillna(0)
		# print(response_data)

		return response_data


	except Exception as e:
		return {"message": str(e)}
