from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from datetime import datetime as dt
import pandas as pd
from db_connect.setup import get_db

analytics_router = APIRouter()

@analytics_router.get("/getcountbylink/")
async def get_count_by_link(username:str, start_time:dt, end_time:dt, db:session=Depends(get_db)):
	"""API to get click counts of all links created by user

	Args:
		username (str): Username
		start_time (dt): start time
		end_time (dt): end time
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		dict: click count for every link created for a user
	"""
	try:
		# Raw SQL query to get all the links (id only) present for a user
		profile_links = db.execute("SELECT Link.id FROM Link, Profile WHERE Profile.id = Link.profile_id AND Profile.username = :uname", {"uname": username})
		links = profile_links.mappings().all()
		if len(links) == 0:
			return JSONResponse(content={"message": "Links not created by user"}, status_code=status.HTTP_404_NOT_FOUND)

		# Raw SQL query to get click count and link name for all the clicks recorded in clicksresample table between given date range for only the list of links queried above
		click_count = db.execute('SELECT ClicksResample.click_count, Link.link_name, ClicksResample.click_sampled_timestamp FROM ClicksResample, Link WHERE Link.id = ClicksResample.link_id AND link_id in :link_list AND click_sampled_timestamp BETWEEN :start AND :end', { 'link_list': tuple(x['id'] for x in links), "start": start_time, "end": end_time })
		click_count = click_count.mappings().all()
		if len(click_count) == 0:
			return JSONResponse(content={"message": "Data not found for the given date range"}, status_code=status.HTTP_404_NOT_FOUND)
		
		click_count_df = pd.DataFrame(click_count)
		# To get the total clicks count for each link
		clicks_grouped_by_link = click_count_df.groupby([click_count_df.link_name])["click_count"].sum()
		# clicks_grouped_by_link.sort_values('click_count', ascending=False, inplace=True) #TODO: To try sorting by counts in descending order
		print(clicks_grouped_by_link)
		# Response formatting
		clicks_response_data = {}
		for index, row in clicks_grouped_by_link.items():
			clicks_response_data[index] = row
		return JSONResponse(content={"data": clicks_response_data}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)