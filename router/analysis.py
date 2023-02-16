from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
import crud.clicks_resample as clicks_resample
import crud.views_resample as views_resample
from crud.profiles import get_profile_by_id
from db_connect.setup import get_db
from db_connect.config import postgre_engine
from datetime import datetime as dt
from sqlalchemy import inspect
from crud import profiles
import json
import numpy as np
import pandas as pd
from utilities.analysis import get_views_and_clicks, get_unique_views_and_clicks, get_activity
from fastapi.encoders import jsonable_encoder

analysis_router = APIRouter()


# return count of all clicks and views gor a profile
# @analysis_router.get("/analysis/")
# async def get(id: int, start: dt = None, end: dt = None, db: session = Depends(get_db)):
#     view_count = 0
#     click_count = 0
#     views = []
#     clicks = []
#     try:
#         _profile = get_profile_by_id(db=db, id=id)
#         if _profile is not None:
#             _views = views_resample.get_views_by_profile_id(db=db, profile_id=_profile.id)
#             views_count = 0
#             for _view in _views:
#                 views_count += _view.view_count
#                 views = _views
#                 _clicks = []
#                 clicks_count = 0
#                 for _view in _views:
#                     _click = clicks_resample.get_click_by_view_id(
#                         db=db, view_id=_view.id)
#                     for c in _click:
#                         _clicks.append(c)
#                         clicks_count += c.click_count
#             clicks = _clicks
#             view_count = views_count
#             click_count = clicks_count
#             if start == None and end == None:
#                     # get starting date of views and clicks
#                 _views_date_wise = {}
#                 for _view in _views:
#                     if _view.view_created.date() in _views_date_wise:
#                         _views_date_wise[_view.view_created.date()] += _view.view_count
#                     else:
#                         _views_date_wise[_view.view_created.date()] = _view.view_count
        
#                 _views_keys = list(_views_date_wise.keys())
#                 _views_keys.sort()
#                 _views_date_wise = {i: _views_date_wise[i] for i in _views_keys}
#                 start = list(_views_date_wise.keys())[0]
#                 end = list(_views_date_wise.keys())[-1]
#                 dates = []
#                 # add all dates between start and end to dates list
#                 for i in range((end-start).days+1):
#                     dates.append(start+datetime.timedelta(days=i))
#                 for date in dates:
#                     if date not in _views_date_wise:
#                         _views_date_wise[date] = 0
#                 _clicks_date_wise = {}
#                 for _click in _clicks:
#                     if _click.click_sampled_timestamp.date() in _clicks_date_wise:
#                         _clicks_date_wise[_click.click_sampled_timestamp.date()] += _click.click_count
#                     else:
#                         _clicks_date_wise[_click.click_sampled_timestamp.date()] = _click.click_count
#                 _clicks_keys = list(_clicks_date_wise.keys())
#                 _clicks_keys.sort()
#                 _clicks_date_wise = {i: _clicks_date_wise[i] for i in _clicks_keys}
#                 for date in dates:
#                     if date not in _clicks_date_wise:
#                         _clicks_date_wise[date] = 0
#                 return ResponseClick(code=status.HTTP_200_OK, status="OK", result={"clicks": {"click_count": click_count, "click": _clicks_date_wise}, "views": {"view_count": view_count, "view": _views_date_wise}}, message="Success").dict(exclude_none=True)
#             elif start != None and end != None:
#                 start = start.date()
#                 end = end.date()
#                 dates = []
#                 # add all dates between start and end to dates list
#                 for i in range((end-start).days+1):
#                     dates.append(start+datetime.timedelta(days=i))
#                 _views_date_wise = {}
#                 for _view in _views:
#                     if start <= _view.view_created.date() and end >= _view.view_created.date():
#                         if start <= _view.view_created.date() and start <= _view.view_created.date() and _view.view_created.date() in _views_date_wise:
#                             _views_date_wise[_view.view_created.date()
#                                             ] += _view.view_count
#                         else:
#                             _views_date_wise[_view.view_created.date()
#                                             ] = _view.view_count
#                 for date in dates:
#                     if date not in _views_date_wise:
#                         _views_date_wise[date] = 0
#                 view_keys = list(_views_date_wise.keys())
#                 view_keys.sort()
#                 _views_date_wise = {i: _views_date_wise[i] for i in view_keys}
#                 _clicks_date_wise = {}
#                 for _click in _clicks:
#                     if start <= _click.click_created.date() and end >= _click.click_created.date():
#                         if start <= _click.click_created.date() and start <= _click.click_created.date() and _click.click_created.date() in _clicks_date_wise:
#                             _clicks_date_wise[_click.click_created.date()
#                                             ] += _click.click_count
#                         else:
#                             _clicks_date_wise[_click.click_created.date()
#                                             ] = _click.click_count
#                 for date in dates:
#                     if date not in _clicks_date_wise:
#                         _clicks_date_wise[date] = 0
#                 click_keys = list(_clicks_date_wise.keys())
#                 click_keys.sort()
#                 _clicks_date_wise = {i: _clicks_date_wise[i] for i in click_keys}
#                 return ResponseClick(code=status.HTTP_200_OK, status="OK", result={"clicks": {"click_count": click_count, "click": _clicks_date_wise}, "views": {"view_count": view_count, "view": _views_date_wise}}, message="Success").dict(exclude_none=True)
#             elif start == None and end != None:
#                 end = end.date()
#                 _views_date_wise = {}
#                 for _view in _views:
#                     if _view.view_created.date() <= end:
#                         if _view.view_created.date() in _views_date_wise:
#                             _views_date_wise[_view.view_created.date()
#                                             ] += _view.view_count
#                         else:
#                             _views_date_wise[_view.view_created.date()
#                                             ] = _view.view_count
#                 # sort
#                 _views_keys = list(_views_date_wise.keys())
#                 _views_keys.sort()
#                 _views_date_wise = {i: _views_date_wise[i] for i in _views_keys}
#                 start = list(_views_date_wise.keys())[0]
#                 dates = []
#                 # add all dates between start and end to dates list
#                 for i in range((end-start).days+1):
#                     dates.append(start+datetime.timedelta(days=i))
#                 for date in dates:
#                     if date not in _views_date_wise:
#                         _views_date_wise[date] = 0
#                 _clicks_date_wise = {}
#                 for _click in _clicks:
#                     if _click.click_created.date() <= end:
#                         if _click.click_created.date() in _clicks_date_wise:
#                             _clicks_date_wise[_click.click_created.date()
#                                             ] += _click.click_count
#                         else:
#                             _clicks_date_wise[_click.click_created.date()
#                                             ] = _click.click_count
#                 _clicks_keys = list(_clicks_date_wise.keys())
#                 _clicks_keys.sort()
#                 _clicks_date_wise = {i: _clicks_date_wise[i] for i in _clicks_keys}
#                 for date in dates:
#                     if date not in _clicks_date_wise:
#                         _clicks_date_wise[date] = 0
#                 return ResponseClick(code=status.HTTP_200_OK, status="OK", result={"clicks": {"click_count": click_count, "click": _clicks_date_wise}, "views": {"view_count": view_count, "view": _views_date_wise}}, message="Success").dict(exclude_none=True)
#             elif start != None and end == None:
#                 start = start.date()
#                 _views_date_wise = {}
#                 for _view in _views:
#                     if _view.view_created.date() >= start:
#                         if _view.view_created.date() in _views_date_wise:
#                             _views_date_wise[_view.view_created.date()
#                                             ] += _view.view_count
#                         else:
#                             _views_date_wise[_view.view_created.date()
#                                             ] = _view.view_count
#                 # sort
#                 _views_keys = list(_views_date_wise.keys())
#                 _views_keys.sort()
#                 _views_date_wise = {i: _views_date_wise[i] for i in _views_keys}
#                 end = list(_views_date_wise.keys())[-1]
#                 dates = []
#                 # add all dates between start and end to dates list
#                 for i in range((end-start).days+1):
#                     dates.append(start+datetime.timedelta(days=i))
#                 for date in dates:
#                     if date not in _views_date_wise:
#                         _views_date_wise[date] = 0
#                 _clicks_date_wise = {}
#                 for _click in _clicks:
#                     if _click.click_created.date() >= start:
#                         if _click.click_created.date() in _clicks_date_wise:
#                             _clicks_date_wise[_click.click_created.date()
#                                             ] += _click.click_count
#                         else:
#                             _clicks_date_wise[_click.click_created.date()
#                                             ] = _click.click_count
#                 _clicks_keys = list(_clicks_date_wise.keys())
#                 _clicks_keys.sort()
#                 _clicks_date_wise = {i: _clicks_date_wise[i] for i in _clicks_keys}
#                 for date in dates:
#                     if date not in _clicks_date_wise:
#                         _clicks_date_wise[date] = 0
#                 return JSONResponse(code=status.HTTP_200_OK, status="OK", result={"clicks": {"click_count": click_count, "click": _clicks_date_wise}, "views": {"view_count": view_count, "view": _views_date_wise}}, message="Success").dict(exclude_none=True)
#             else:
#                 return JSONResponse(code=status.HTTP_404_NOT_FOUND, status="Not Found", result={}, message="Profile not found")
#     except:
#         return JSONResponse(content={"message": f"Profile {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
## return count of  views and clicks using pandas

# @analysis_router.get("/analysis/activity")
# async def get(username: str, start: dt, end: dt, db: session = Depends(get_db)):
#     try:
#         usernames = profiles.get_all_usernames(db)
#         if username not in usernames:
#             return JSONResponse(content={"message": f"Profile {username} not found"}, status_code=status.HTTP_404_NOT_FOUND)

#         if not start and not end:
#             return JSONResponse(content={"message": f"Date range should be provided"}, status_code=status.HTTP_400_BAD_REQUEST)
#         profile_id = profiles.get_profile_by_user(db, username)
#         views = db.execute("SELECT * FROM ViewsResample WHERE ViewsResample.profile_id = profile_id AND view_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         _views_df = pd.DataFrame(views.fetchall())
#         print(_views_df)
#         view_ids = list(_views_df["id"])
#         # print viewsresample id from _views_df
#         # print(_views_df["id"])
#         # view_ids = db.execute("SELECT * from ViewsResample WHERE ViewsResample.profile_id = profile_id AND view_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         # view_ids = pd.DataFrame(view_ids.fetchall())
#         print(view_ids)
#         return JSONResponse(content={"msg":"msg"})
    # except:
    #     return JSONResponse(content={"msg":"error"})

# @analysis_router.get("/analytics/getactivitycountbyfrequency/")
# async def get(username: str, start: dt, end: dt, db: session = Depends(get_db)):
#     try:
#         usernames = profiles.get_all_usernames(db)
#         if username not in usernames:
#             return JSONResponse(content={"message": f"Profile {username} not found"}, status_code=status.HTTP_404_NOT_FOUND)
#         if not start or not end:
#             return JSONResponse(content={"message": f"Date range should be provided"}, status_code=status.HTTP_400_BAD_REQUEST)
#         views = db.execute("SELECT * FROM ViewsResample, Profile WHERE ViewsResample.profile_id = Profile.id AND Profile.username = :username AND view_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         _views_df = pd.DataFrame(views.fetchall())
#         if _views_df.empty:
#             return JSONResponse(content={"message": f"No data found for the specified date range"}, status_code=status.HTTP_404_NOT_FOUND)
#         # _views_df.columns = views_table.keys() # not needed
#         # view_ids = list(_views_df["id"]) gives the same output as below
#         view_ids = []
#         for view in _views_df["id"]:
#             view_ids.append(view)
#         print(view_ids)
#         _views_df["view_sampled_timestamp"] = pd.to_datetime(_views_df["view_sampled_timestamp"])
#         _views_table = pd.pivot_table(_views_df, values='view_count', index=['view_sampled_timestamp'], columns=['session_id']).fillna(0)
#         views_table = _views_table.resample('D').sum()
#         fieldnames = views_table.columns
#         # views_table = views_table.reset_index()
#         views_table.index = views_table.index.strftime('%Y-%m-%d')
#         views_response_data = {}
#         # gives a cleaner response structure
#         for index, row in views_table.iterrows():
#             views_response_data[index] = []
#             for session in fieldnames:
#                 views_response_data[index].append({"session_id": session, "view_count": int(row[session])})
#         # views_response_data = json.loads(views_table.to_json(orient='records'))
#         # Use dict_variable.items() to iterate through the dictionary
#         # for i in range(len(views_response_data)):
#         #     for k,v in views_response_data[i].items():
#         #         if k!= "view_sampled_timestamp":
#         #             views_response_data[i][k] = {"session_id": k, "view_count": v}
#         # with postgre_engine.connect() as conn:
#         #     query = f"SELECT * FROM ClicksResample WHERE view_id = {view_ids[0]} AND click_sampled_timestamp BETWEEN '{start}' AND '{end}'"
#         #     clicks_table = conn.execute(query)
#         # _clicks_df = pd.DataFrame(clicks_table.fetchall())
#         # _clicks_df.columns = clicks_table.keys()
#         # for view_id in view_ids[1:]:
#         #     with postgre_engine.connect() as conn:
#         #         query = f"SELECT * FROM ClicksResample WHERE view_id = {view_id} AND click_sampled_timestamp BETWEEN '{start}' AND '{end}'"
#         #         clicks_table = conn.execute(query)
#         #     _click_df = pd.DataFrame(clicks_table.fetchall())
#         #     _click_df.columns = clicks_table.keys()
#         #     _clicks_df = _clicks_df.append(_click_df)
#         clicks = db.execute("SELECT * FROM ClicksResample, ViewsResample WHERE ViewsResample.id = ClicksResample.view_id AND view_id in :views_list AND click_sampled_timestamp BETWEEN :start AND :end", {"views_list": tuple(view_ids), "start": start, "end": end})
#         _clicks_df = pd.DataFrame(clicks.fetchall())
#         _clicks_df["click_sampled_timestamp"] = pd.to_datetime(_clicks_df["click_sampled_timestamp"])
#         # dataframe needs to be grouped by unique date and view to get their corresponding counts
#         clicks_grouped_by_date = _clicks_df.groupby([_clicks_df.click_sampled_timestamp.dt.date, _clicks_df.view_id])["click_count"].sum()
#         clicks_response_data = {}
#         for index, row in clicks_grouped_by_date.items():
#             if index[0].strftime('%Y-%m-%d') in clicks_response_data.keys():
#                 clicks_response_data[index[0].strftime('%Y-%m-%d')].append({"view_id": index[1], "click_count": row})
#             else:
#                 clicks_response_data[index[0].strftime('%Y-%m-%d')] = [{"view_id": index[1], "click_count": row}]
        
#         return JSONResponse(content={"message": {"views": views_response_data, "clicks": clicks_response_data}}, status_code=status.HTTP_200_OK)
#     except Exception as e:
#         return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


# views group by view_id
# clicks group by link_id
# add doc string to the function
# add comments to the code




# get the unique views and unique clicks for the profile with username in date range
# @analysis_router.get("/analytics/getuniqueactivitycount/")
# async def get(username:str, start:dt, end:dt, db:session=Depends(get_db)):
#     try:
#         usernames = profiles.get_all_usernames(db)
#         if username not in usernames:
#             return JSONResponse(content={"message": f"User with username {username} not found"}, status_code=status.HTTP_404_NOT_FOUND)
#         if not start or not end:
#             return JSONResponse(content={"message": "start and end dates are required"}, status_code=status.HTTP_400_BAD_REQUEST)
#         # a view is a unique_view if it has a unique session_id
#         _views = db.execute("SELECT COUNT(DISTINCT session_id) FROM ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND view_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         unique_views = _views.fetchone()[0]
#         if unique_views == 0:
#             return JSONResponse(content={"message": "no views found"}, status_code=status.HTTP_400_BAD_REQUEST)
#         # print(unique_views)
#         # differentiate unique_views by date
#         views_by_date = {}
#         views = db.execute("SELECT DISTINCT session_id, view_sampled_timestamp FROM ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND view_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         _views_df = pd.DataFrame(views.fetchall())
#         if _views_df.empty:
#             return JSONResponse(content={"message": "no views found"}, status_code=status.HTTP_400_BAD_REQUEST)
#         _views_df["view_sampled_timestamp"] = pd.to_datetime(_views_df["view_sampled_timestamp"])
#         views_grouped_by_date = _views_df.groupby(_views_df.view_sampled_timestamp.dt.date)["session_id"].nunique()
#         for index, row in views_grouped_by_date.items():
#             views_by_date[index.strftime('%Y-%m-%d')] = row
#         views_response_data = {}
#         views_response_data["unique_views_by_date"] = views_by_date
#         # a click is a unique_click if it has a unique session_id with respect to the view_id in ViewsResample and a unique link_id
#         _clicks = db.execute("SELECT COUNT(DISTINCT session_id) FROM ClicksResample, ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND ViewsResample.id = ClicksResample.view_id AND click_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         unique_clicks = _clicks.fetchone()[0]
#         # print(unique_clicks)
#         if unique_clicks == 0:
#             return JSONResponse(content={"message": "no clicks found"}, status_code=status.HTTP_400_BAD_REQUEST)
#         clicks_by_date = {}
#         clicks = db.execute("SELECT DISTINCT session_id, click_sampled_timestamp FROM ClicksResample, ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND ViewsResample.id = ClicksResample.view_id AND click_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         _clicks_df = pd.DataFrame(clicks.fetchall())
#         _clicks_df["click_sampled_timestamp"] = pd.to_datetime(_clicks_df["click_sampled_timestamp"])
#         clicks_grouped_by_date = _clicks_df.groupby(_clicks_df.click_sampled_timestamp.dt.date)["session_id"].nunique()
#         for index, row in clicks_grouped_by_date.items():
#             clicks_by_date[index.strftime('%Y-%m-%d')] = row
#         clicks_response_data = {}
#         clicks_response_data["unique_clicks_by_date"] = clicks_by_date
#         return JSONResponse(content={"views": views_response_data, "clicks": clicks_response_data}, status_code=status.HTTP_200_OK)
#     except Exception as e:
#         return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

# def get_unique_views_and_clicks(username: str, start: dt, end: dt, db:session=Depends(get_db)):
#     try:
#         # a view is a unique_view if it has a unique session_id
#         _views = db.execute("SELECT COUNT(DISTINCT session_id) FROM ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND view_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         unique_views = _views.fetchone()[0]
#         if unique_views == 0:
#             return JSONResponse(content={"unique_views": 0, "unique_clicks": 0}, status_code=status.HTTP_200_OK)
#         # print(unique_views)
#         # differentiate unique_views by date
#         views_by_date = {}
#         views = db.execute("SELECT DISTINCT session_id, view_sampled_timestamp FROM ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND view_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         _views_df = pd.DataFrame(views.fetchall())
#         if _views_df.empty:
#             return JSONResponse(content={"message": "no views found"}, status_code=status.HTTP_400_BAD_REQUEST)
#         _views_df["view_sampled_timestamp"] = pd.to_datetime(_views_df["view_sampled_timestamp"])
#         views_grouped_by_date = _views_df.groupby(_views_df.view_sampled_timestamp.dt.date)["session_id"].nunique()
#         for index, row in views_grouped_by_date.items():
#             views_by_date[index.strftime('%Y-%m-%d')] = row
#         views_response_data = {}
#         views_response_data["unique_views_by_date"] = views_by_date
#         # a click is a unique_click if it has a unique session_id with respect to the view_id in ViewsResample and a unique link_id
#         _clicks = db.execute("SELECT COUNT(DISTINCT session_id) FROM ClicksResample, ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND ViewsResample.id = ClicksResample.view_id AND click_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         unique_clicks = _clicks.fetchone()[0]
#         # print(unique_clicks)
#         if unique_clicks == 0:
#             return JSONResponse(content={"message": "no clicks found"}, status_code=status.HTTP_400_BAD_REQUEST)
#         clicks_by_date = {}
#         clicks = db.execute("SELECT DISTINCT session_id, click_sampled_timestamp FROM ClicksResample, ViewsResample, Profile WHERE Profile.id = ViewsResample.profile_id AND Profile.username = :username AND ViewsResample.id = ClicksResample.view_id AND click_sampled_timestamp BETWEEN :start AND :end", {"username": username, "start": start, "end": end})
#         _clicks_df = pd.DataFrame(clicks.fetchall())
#         _clicks_df["click_sampled_timestamp"] = pd.to_datetime(_clicks_df["click_sampled_timestamp"])
#         clicks_grouped_by_date = _clicks_df.groupby(_clicks_df.click_sampled_timestamp.dt.date)["session_id"].nunique()
#         for index, row in clicks_grouped_by_date.items():
#             clicks_by_date[index.strftime('%Y-%m-%d')] = row
#         clicks_response_data = {}
#         clicks_response_data["unique_clicks_by_date"] = clicks_by_date
#         return {"views": views_response_data, "clicks": clicks_response_data}
#     except Exception as e:
#         return {"message": str(e)}

# def get_views_and_clicks(username: str, start: dt, end: dt, db : session = Depends(get_db)):
#     try:
#         profile_id = profiles.get_profile_by_user(db, username)
#         views = db.execute("SELECT * FROM ViewsResample WHERE ViewsResample.profile_id = profile_id AND view_sampled_timestamp BETWEEN :start AND :end", {"start": start, "end": end})
#         _views_df = pd.DataFrame(views.fetchall())
#         print(_views_df)
#         if _views_df.empty:
#             return JSONResponse(content={"message": f"No data found for the specified date range"}, status_code=status.HTTP_404_NOT_FOUND)
#         # get all view_ids
#         view_ids = list(_views_df["id"])
#         print(view_ids)
#         _views_df["view_sampled_timestamp"] = pd.to_datetime(_views_df["view_sampled_timestamp"])
#         _views_table = pd.pivot_table(_views_df, values='view_count', index=['view_sampled_timestamp'], columns=['session_id']).fillna(0)
#         views_table = _views_table.resample('D').sum()
#         fieldnames = views_table.columns
#         # views_table = views_table.reset_index()
#         views_table.index = views_table.index.strftime('%Y-%m-%d')
#         views_response_data = {}
#         # gives a cleaner response structure
#         for index, row in views_table.iterrows():
#             views_response_data[index] = []
#             for session in fieldnames:
#                 views_response_data[index].append({"session_id": session, "view_count": int(row[session])})
#         clicks = db.execute("SELECT * FROM ClicksResample, ViewsResample WHERE ViewsResample.id = ClicksResample.view_id AND view_id in :views_list AND click_sampled_timestamp BETWEEN :start AND :end", {"views_list": tuple(view_ids), "start": start, "end": end})
#         _clicks_df = pd.DataFrame(clicks.fetchall())
#         _clicks_df["click_sampled_timestamp"] = pd.to_datetime(_clicks_df["click_sampled_timestamp"])
#         # dataframe needs to be grouped by unique date and view to get their corresponding counts
#         clicks_grouped_by_date = _clicks_df.groupby([_clicks_df.click_sampled_timestamp.dt.date, _clicks_df.view_id])["click_count"].sum()
#         clicks_response_data = {}
#         for index, row in clicks_grouped_by_date.items():
#             if index[0].strftime('%Y-%m-%d') in clicks_response_data.keys():
#                 clicks_response_data[index[0].strftime('%Y-%m-%d')].append({"view_id": index[1], "click_count": row})
#             else:
#                 clicks_response_data[index[0].strftime('%Y-%m-%d')] = [{"view_id": index[1], "click_count": row}]
        
#         return {"views": views_response_data, "clicks": clicks_response_data}
#     except Exception as e:
#         return {"message": str(e)}


# wrap all the functions in a single router
# @analysis_router.get("/analytics/getactivitycount")
# async def get_activity_count(username: str, start: dt, end: dt, db:session=Depends(get_db)):
#     try:
#         usernames = profiles.get_all_usernames(db)
#         if username not in usernames:
#             return JSONResponse(content={"message": f"User with username {username} not found"}, status_code=status.HTTP_404_NOT_FOUND)
#         if not start or not end:
#             return JSONResponse(content={"message": "start and end dates are required"}, status_code=status.HTTP_400_BAD_REQUEST)
#         # get total views for a date
#         views_and_clicks = get_views_and_clicks(username, start, end, db)
#         print(views_and_clicks)
#         response_data = {"data": []}
#         for date, view in views_and_clicks["views"].items():
#             view_count=0
#             for session in view:
#                 view_count+=session["view_count"]
#             response_data["data"].append({"date": date, "views": view_count})
        
#         for date, clicks in views_and_clicks["clicks"].items():
#             click_count=0
#             for click in clicks:
#                 click_count+=click["click_count"]
#             temp=False
#             for i in range(len(response_data["data"])):
#                 if date == response_data["data"][i]["date"]:
#                     response_data["data"][i]["clicks"] = click_count
#                     temp=True
#                     break
#         for i in range(len(response_data["data"])):
#             if response_data["data"][i].get("views")==None and response_data["data"][i].get("clicks")==None:
#                 response_data["data"][i]["ctr"]=0
#                 response_data["data"][i]["views"]=0
#                 response_data["data"][i]["clicks"]=0
#             elif response_data["data"][i].get("views")==None:
#                 response_data["data"][i]["views"]=0
#                 response_data["data"][i]["ctr"]=0
#             elif response_data["data"][i].get("clicks")==None:
#                 response_data["data"][i]["clicks"]=0
#                 response_data["data"][i]["ctr"]=0
#             elif response_data["data"][i].get("views")!=None and response_data["data"][i].get("clicks")!=None:
#                 response_data["data"][i]["ctr"] = round(response_data["data"][i]["clicks"]/response_data["data"][i]["views"], 3)
#         unique_views_and_clicks = get_unique_views_and_clicks(username, start, end, db)
#         for i in range(len(response_data["data"])):
#             response_data["data"][i]["unique_views"] = unique_views_and_clicks["views"]["unique_views_by_date"][response_data["data"][i]["date"]]
#             # response_data["data"][i]["unique_clicks"] = unique_views_and_clicks["clicks"]["unique_clicks_by_date"][response_data["data"][i]["date"]]
#         for i in range(len(response_data["data"])):
#             if response_data["data"][i]["date"] in unique_views_and_clicks["clicks"]["unique_clicks_by_date"]:
#                 response_data["data"][i]["unique_clicks"] = unique_views_and_clicks["clicks"]["unique_clicks_by_date"][response_data["data"][i]["date"]]
#             else:
#                 response_data["data"][i]["unique_clicks"] = 0
#         return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
#     except Exception as e:
#         return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
        

@analysis_router.get("/analytics/getactivitycount")
async def get_activity_test(username: str, start: dt, end: dt, freq: str, db:session=Depends(get_db)):
    try:
        usernames = profiles.get_all_usernames(db)
        if username not in usernames:
            return JSONResponse(content={"message": f"User with username {username} not found"}, status_code=status.HTTP_404_NOT_FOUND)
        if not start or not end:
            return JSONResponse(content={"message": "start and end dates are required"}, status_code=status.HTTP_400_BAD_REQUEST)
        if start>end:
            return JSONResponse(content={"message": "start date should be less than end date"}, status_code=status.HTTP_400_BAD_REQUEST)
        if freq not in ["daily", "weekly", "monthly"]:
            return JSONResponse(content={"message": "freq should be daily, weekly or monthly"}, status_code=status.HTTP_400_BAD_REQUEST)
        
        response_data = get_activity(username, start, end, freq, db)
        # response_data = response_data.to_dict(orient="records")
        # response_data = json.dumps(response_data, default=str)
        # response_data = {"data": response_data}
        # response_data = json.loads(response_data["data"])
        response_data = pd.DataFrame(response_data)
        response_data = response_data.groupby("date").sum().reset_index()
        # iterrows to get ctr using loop
        response_data["ctr"] = [0 if row["total_views"]==0 else round(row["total_clicks"]/row["total_views"]*100, 3) for index, row in response_data.iterrows()]
        response_data = response_data.to_dict(orient="records")
        response_data = json.dumps(response_data, default=str)
        response_data = {"data": response_data}
        response_data = json.loads(response_data["data"])
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@analysis_router.get("/analytics/getmetrics/")
async def get(username:str, db:session=Depends(get_db)):
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
