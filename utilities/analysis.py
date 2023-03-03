import pandas as pd


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
