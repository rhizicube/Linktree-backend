from fastapi import Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from db_connect.setup import get_db
from datetime import datetime as dt
from crud import profiles
import pandas as pd
def get_unique_views_and_clicks(username: str, start: dt, end: dt, db:session=Depends(get_db)):
    try:
        # a view is a unique_view if it has a unique session_id
        _views = db.execute("SELECT COUNT(DISTINCT session_id) FROM ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND view_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
        unique_views = _views.fetchone()[0]
        if unique_views == 0:
            return JSONResponse(content={"unique_views": 0, "unique_clicks": 0}, status_code=status.HTTP_200_OK)
        # print(unique_views)
        # differentiate unique_views by date
        views_by_date = {}
        views = db.execute("SELECT DISTINCT session_id, view_sampled_timestamp FROM ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND view_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
        _views_df = pd.DataFrame(views.fetchall())
        if _views_df.empty:
            return JSONResponse(content={"message": "no views found"}, status_code=status.HTTP_400_BAD_REQUEST)
        _views_df["view_sampled_timestamp"] = pd.to_datetime(_views_df["view_sampled_timestamp"])
        views_grouped_by_date = _views_df.groupby(_views_df.view_sampled_timestamp.dt.date)["session_id"].nunique()
        for index, row in views_grouped_by_date.items():
            views_by_date[index.strftime('%Y-%m-%d')] = row
        views_response_data = {}
        views_response_data["unique_views_by_date"] = views_by_date
        # a click is a unique_click if it has a unique session_id with respect to the view_id in ViewsResample and a unique link_id
        _clicks = db.execute("SELECT COUNT(DISTINCT session_id) FROM ClicksResample, ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND ViewsResample.id = ClicksResample.view_id AND click_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
        unique_clicks = _clicks.fetchone()[0]
        # print(unique_clicks)
        if unique_clicks == 0:
            return JSONResponse(content={"message": "no clicks found"}, status_code=status.HTTP_400_BAD_REQUEST)
        clicks_by_date = {}
        clicks = db.execute("SELECT DISTINCT session_id, click_sampled_timestamp FROM ClicksResample, ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND ViewsResample.id = ClicksResample.view_id AND click_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
        _clicks_df = pd.DataFrame(clicks.fetchall())
        _clicks_df["click_sampled_timestamp"] = pd.to_datetime(_clicks_df["click_sampled_timestamp"])
        clicks_grouped_by_date = _clicks_df.groupby(_clicks_df.click_sampled_timestamp.dt.date)["session_id"].nunique()
        for index, row in clicks_grouped_by_date.items():
            clicks_by_date[index.strftime('%Y-%m-%d')] = row
        clicks_response_data = {}
        clicks_response_data["unique_clicks_by_date"] = clicks_by_date
        return {"views": views_response_data, "clicks": clicks_response_data}
    except Exception as e:
        return {"message": str(e)}

def get_views_and_clicks(username: str, start: dt, end: dt, db : session = Depends(get_db)):
    try:
        profile_id = profiles.get_profile_by_user(db, username)
        views = db.execute("SELECT * FROM ViewsResample WHERE ViewsResample.profile_id = profile_id AND view_sampled_timestamp BETWEEN :start AND :end", {"start": start, "end": end})
        _views_df = pd.DataFrame(views.fetchall())
        print(_views_df)
        if _views_df.empty:
            return JSONResponse(content={"message": f"No data found for the specified date range"}, status_code=status.HTTP_404_NOT_FOUND)
        # get all view_ids
        view_ids = list(_views_df["id"])
        print(view_ids)
        _views_df["view_sampled_timestamp"] = pd.to_datetime(_views_df["view_sampled_timestamp"])
        _views_table = pd.pivot_table(_views_df, values='view_count', index=['view_sampled_timestamp'], columns=['session_id']).fillna(0)
        views_table = _views_table.resample('D').sum()
        fieldnames = views_table.columns
        # views_table = views_table.reset_index()
        views_table.index = views_table.index.strftime('%Y-%m-%d')
        views_response_data = {}
        # gives a cleaner response structure
        for index, row in views_table.iterrows():
            views_response_data[index] = []
            for session in fieldnames:
                views_response_data[index].append({"session_id": session, "view_count": int(row[session])})
        clicks = db.execute("SELECT * FROM ClicksResample, ViewsResample WHERE ViewsResample.id = ClicksResample.view_id AND view_id in :views_list AND click_sampled_timestamp BETWEEN :start AND :end", {"views_list": tuple(view_ids), "start": start, "end": end})
        _clicks_df = pd.DataFrame(clicks.fetchall())
        _clicks_df["click_sampled_timestamp"] = pd.to_datetime(_clicks_df["click_sampled_timestamp"])
        # dataframe needs to be grouped by unique date and view to get their corresponding counts
        clicks_grouped_by_date = _clicks_df.groupby([_clicks_df.click_sampled_timestamp.dt.date, _clicks_df.view_id])["click_count"].sum()
        clicks_response_data = {}
        for index, row in clicks_grouped_by_date.items():
            if index[0].strftime('%Y-%m-%d') in clicks_response_data.keys():
                clicks_response_data[index[0].strftime('%Y-%m-%d')].append({"view_id": index[1], "click_count": row})
            else:
                clicks_response_data[index[0].strftime('%Y-%m-%d')] = [{"view_id": index[1], "click_count": row}]
        
        return {"views": views_response_data, "clicks": clicks_response_data}
    except Exception as e:
        return {"message": str(e)}
