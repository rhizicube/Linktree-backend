from fastapi import Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from db_connect.setup import get_db
from datetime import datetime as dt
from crud import profiles
import pandas as pd
import json
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
