from sqlalchemy.orm import session
from db_connect.setup import get_db
from datetime import datetime as dt
from crud import profiles
import pandas as pd


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

def get_views_total_unique(_views_df:pd.DataFrame) -> tuple:
	"""Function to get total and unique view counts

	Args:
		_views_df (pd.DataFrame): ViewsResample details of a profile

	Returns:
		tuple: dataframe of total views and unique views
	"""
	_views_df["view_sampled_timestamp"] = pd.to_datetime(_views_df["view_sampled_timestamp"])
	views_grouped_by_date = _views_df.groupby([_views_df.view_sampled_timestamp.dt.date])["view_count"].sum() # To get the total views grouped by date
	views_unique_grouped_by_date = _views_df.groupby([_views_df.view_sampled_timestamp.dt.date])["id"].nunique() # To get the unique views grouped by date
	return views_grouped_by_date, views_unique_grouped_by_date


def get_clicks_total_unique(_clicks_df:pd.DataFrame) -> tuple:
	"""Function to get total and unique view counts

	Args:
		_clicks_df (pd.DataFrame): ClicksResample details of a profile

	Returns:
		tuple: dataframe of total views and unique views
	"""
	_clicks_df["click_sampled_timestamp"] = pd.to_datetime(_clicks_df["click_sampled_timestamp"])
	# To get the total clicks grouped by date
	clicks_grouped_by_date = _clicks_df.groupby([_clicks_df.click_sampled_timestamp.dt.date])["click_count"].sum()
	# To get unique clicks grouped by date and view id
	clicks_unique_grouped_by_date_view = _clicks_df.groupby([_clicks_df.click_sampled_timestamp.dt.date, _clicks_df.view_id])["link_id"].nunique()
	clicks_unique_grouped_by_date_view = clicks_unique_grouped_by_date_view.reset_index()
	clicks_unique_grouped_by_date_view.click_sampled_timestamp = pd.to_datetime(clicks_unique_grouped_by_date_view.click_sampled_timestamp)
	clicks_unique_grouped_by_date_view = clicks_unique_grouped_by_date_view.resample('D', on="click_sampled_timestamp").agg({"link_id": "sum"})
	return clicks_grouped_by_date, clicks_unique_grouped_by_date_view


def merge_total_unique_views_clicks(views_grouped_by_date:pd.DataFrame, clicks_grouped_by_date:pd.DataFrame, views_unique_grouped_by_date:pd.DataFrame, clicks_unique_grouped_by_date_view:pd.DataFrame) -> dict:
	"""Function to merge total views, total clicks, unique views and unique clicks, sample by day, week and month, and determine the CTR for each

	Args:
		views_grouped_by_date (pd.DataFrame): Total views
		clicks_grouped_by_date (pd.DataFrame): Total clicks
		views_unique_grouped_by_date (pd.DataFrame): Unique views
		clicks_unique_grouped_by_date_view (pd.DataFrame): Unique clicks

	Returns:
		dict: daily, weekly and monthly sampled total/unique views/clicks with their corresponding CTR
	"""
	if clicks_grouped_by_date.empty:
		# Case when no links or clicks are present
		view_click_merge_df = pd.concat([views_grouped_by_date, views_unique_grouped_by_date], axis=1)
		view_click_merge_df["click_count"] = 0
		view_click_merge_df["link_id"] = 0
	else:
		view_click_merge_df = pd.concat([views_grouped_by_date, clicks_grouped_by_date, views_unique_grouped_by_date], axis=1)
	view_click_merge_df.index = pd.to_datetime(view_click_merge_df.index)
	view_click_merge_df = pd.concat([view_click_merge_df, clicks_unique_grouped_by_date_view], axis=1).fillna(0)
	view_click_merge_df.rename(columns={"view_count": "total_views", "click_count": "total_clicks", "id": "unique_views", "link_id": "unique_clicks"}, inplace=True)
	resampling_types = {"total_views": "sum", "total_clicks": "sum", "unique_views": "sum", "unique_clicks": "sum"}
	# Get daily sampled counts
	view_click_group_merge = {"daily": view_click_merge_df.resample('D').agg(resampling_types)}
	# Get weekly sampled counts
	view_click_group_merge["weekly"] = view_click_merge_df.resample('W').agg(resampling_types)
	# Get monthly sampled counts
	view_click_group_merge["monthly"] = view_click_merge_df.resample('M').agg(resampling_types)
	
	# Format according to required response structure
	for key, value in view_click_group_merge.items():
		# CTR is calculated by dividing the number of clicks by how many views your profile has received
		value["ctr"] = [round((row["total_clicks"]/row["total_views"])*100, 3) if row["total_views"] != 0 else 0 for _, row in value.iterrows()]
		value["date"] = value.index.astype('str')
		view_click_group_merge[key] = value.to_dict(orient="records")
	return view_click_group_merge


def get_location_wise_counts(count_df:pd.DataFrame, groupby_column:str) -> dict:
	"""Function to get view/click counts grouped by country, region and city

	Args:
		count_df (pd.DataFrame): ViewsResample details or ClicksResample details of a profile
		groupby_column (str): Column name for getting the aggregated values

	Returns:
		dict: Country, region and city wise counts
	"""
	count_df.dropna(inplace=True) # If there are any rows having no location information
	# Get country, region and city in separate columns
	count_df["country"] = [x["country"] if x not in [None, "", {}] else None for x in count_df["view_location"]]
	count_df["region"] = [x["region"] if x not in [None, "", {}] else None for x in count_df["view_location"]]
	count_df["city"] = [x["city"] if x not in [None, "", {}] else None for x in count_df["view_location"]]
	# Get count grouped by country, region and city
	count_grouped_by_country = count_df.groupby([count_df.country])[groupby_column].sum()
	count_grouped_by_region = count_df.groupby([count_df.country, count_df.region])[groupby_column].sum().reset_index()
	count_grouped_by_city = count_df.groupby([count_df.region, count_df.city])[groupby_column].sum().reset_index()
	count_data = {"country": count_grouped_by_country.to_dict(), "region": {}, "city": {}}
	# Map region to country
	for _, row in count_grouped_by_region.iterrows():
		if row["country"] in count_data["region"].keys():
			count_data["region"][row["country"]][row["region"]] = row[groupby_column]
		else:
			count_data["region"][row["country"]] = {row["region"]: row[groupby_column]}
	# Map city to region
	for _, row in count_grouped_by_city.iterrows():
		if row["region"] in count_data["city"].keys():
			count_data["city"][row["region"]][row["city"]] = row[groupby_column]
		else:
			count_data["city"][row["region"]] = {row["city"]: row[groupby_column]}
	return count_data



def get_activity(username: str, start: dt, end: dt, freq: str, db : session = get_db()):
	try:
		profile = profiles.get_profile_by_user(db, username)
		profile_id = profile.id
		views = db.execute("SELECT id, session_id, view_count, view_sampled_timestamp FROM ViewsResample WHERE ViewsResample.profile_id = :profile_id AND view_sampled_timestamp BETWEEN :start AND :end", {"profile_id": profile_id, "start": start, "end": end})
		_views_df = pd.DataFrame(views.fetchall())
		if _views_df.empty:
			if freq=="daily":
				freq='D'
			elif freq=="weekly":
				freq='W'
			elif freq=="monthly":
				freq='M'
			response_data = pd.DataFrame(columns=["total_views", "total_clicks", "unique_views", "unique_clicks", "ctr"], index=pd.date_range(start=start, end=end, freq=freq))
			response_data = response_data.fillna(0)
			return response_data
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
		views_grouped_by_date = views_grouped_by_date.reset_index()
		# rename index to date
		views_grouped_by_date = views_grouped_by_date.rename(columns={"index": "date", "view_count": "total_views", "view_sampled_timestamp": "date"})
		print(views_grouped_by_date)
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
		unique_views_grouped_by_date = unique_views_grouped_by_date.reset_index()
		# rename session_id to unique_views
		unique_views_grouped_by_date = unique_views_grouped_by_date.rename(columns={"session_id": "unique_views", "index": "date", "view_sampled_timestamp": "date"})
		print(unique_views_grouped_by_date)
		# return views_grouped_by_date
		# get clicks
		view_ids = list(_views_df["id"])
		# clicks = db.execute("SELECT click_count, link_id, click_sampled_timestamp, view_id FROM ClicksResample, ViewsResample WHERE ViewsResample.id = ClicksResample.view_id AND view_id in :views_list AND click_sampled_timestamp BETWEEN :start AND :end", {"views_list": tuple(view_ids), "start": start, "end": end})
		clicks = db.execute("SELECT click_count, link_id, click_sampled_timestamp, view_id FROM ClicksResample WHERE click_sampled_timestamp BETWEEN :start AND :end", {"start": start, "end": end})
		_clicks_df = pd.DataFrame(clicks.fetchall())
		if _clicks_df.empty:
			# create clicks_response with  three cols date=views_df.date, total_clicks=0, unique_clicks=0
			response_data = pd.concat([views_grouped_by_date, unique_views_grouped_by_date])
			response_data["total_clicks"] = 0
			response_data["unique_clicks"] = 0
			return response_data
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
		unique_clicks_grouped_by_date = unique_clicks_grouped_by_date.reset_index()
		unique_clicks_grouped_by_date = unique_clicks_grouped_by_date.rename(columns={"index": "date", "click_sampled_timestamp": "date"})
		print(unique_clicks_grouped_by_date)
		response_data = pd.concat([views_grouped_by_date, unique_views_grouped_by_date])
		response_data = pd.concat([response_data, clicks_grouped_by_date])
		response_data = pd.concat([response_data, unique_clicks_grouped_by_date])
		response_data = response_data.fillna(0)
		return response_data


	except Exception as e:
		return {"Error message": str(e)}
