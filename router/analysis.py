from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from schemas.clicks_resample import RequestClick, ResponseClick, UpdateClick
import crud.clicks_resample as clicks_resample
import crud.views_resample as views_resample
from crud.profiles import get_profile_by_id
from db_connect.setup import get_db
from datetime import datetime as dt
import datetime
import pandas as pd
analysis_router = APIRouter()


# return count of all clicks and views gor a profile
@analysis_router.get("/analysis/")
async def get(id: int, start: dt = None, end: dt = None, db: session = Depends(get_db)):
    view_count = 0
    click_count = 0
    views = []
    clicks = []
    try:
        _profile = get_profile_by_id(db=db, id=id)
        if _profile is not None:
            _views = views_resample.get_views_by_profile_id(db=db, profile_id=_profile.id)
            views_count = 0
            for _view in _views:
                views_count += _view.view_count
                views = _views
                _clicks = []
                clicks_count = 0
                for _view in _views:
                    _click = clicks_resample.get_click_by_view_id(
                        db=db, view_id=_view.id)
                    for c in _click:
                        _clicks.append(c)
                        clicks_count += c.click_count
            clicks = _clicks
            view_count = views_count
            click_count = clicks_count
            if start != None and end != None:
                start = start.date()
                end = end.date()
                dates = []
                # add all dates between start and end to dates list
                for i in range((end-start).days+1):
                    dates.append(start+datetime.timedelta(days=i))
                _views_date_wise = {}
                for _view in _views:
                    if start <= _view.view_created.date() and end >= _view.view_created.date():
                        if start <= _view.view_created.date() and start <= _view.view_created.date() and _view.view_created.date() in _views_date_wise:
                            _views_date_wise[_view.view_created.date()
                                            ] += _view.view_count
                        else:
                            _views_date_wise[_view.view_created.date()
                                            ] = _view.view_count
                for date in dates:
                    if date not in _views_date_wise:
                        _views_date_wise[date] = 0
                view_keys = list(_views_date_wise.keys())
                view_keys.sort()
                _views_date_wise = {i: _views_date_wise[i] for i in view_keys}
                _clicks_date_wise = {}
                for _click in _clicks:
                    if start <= _click.click_created.date() and end >= _click.click_created.date():
                        if start <= _click.click_created.date() and start <= _click.click_created.date() and _click.click_created.date() in _clicks_date_wise:
                            _clicks_date_wise[_click.click_created.date()
                                            ] += _click.click_count
                        else:
                            _clicks_date_wise[_click.click_created.date()
                                            ] = _click.click_count
                for date in dates:
                    if date not in _clicks_date_wise:
                        _clicks_date_wise[date] = 0
                click_keys = list(_clicks_date_wise.keys())
                click_keys.sort()
                _clicks_date_wise = {i: _clicks_date_wise[i] for i in click_keys}
                return ResponseClick(code=status.HTTP_200_OK, status="OK", result={"clicks": {"click_count": click_count, "click": _clicks_date_wise}, "views": {"view_count": view_count, "view": _views_date_wise}}, message="Success").dict(exclude_none=True)
            else:
                return JSONResponse(code=status.HTTP_404_NOT_FOUND, status="Not Found", result={}, message="Profile not found")
    except:
        return JSONResponse(content={"message": f"Profile {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)


## return count of  views and clicks using pandas
# @analysis_router.get("/analysis/")
# async def get(id: int, start: dt = None, end: dt = None, db: session = Depends(get_db)):
#     try:
#         _profile = get_profile_by_id(db=db, id=id)
#         # return _profile
#         _views = views_resample.get_views_by_profile_id(db, id)
#         views_count = []
#         views_created = []
#         for _view in _views:
#             views_count.append(_view.view_count)
#             views_created.append(_view.view_created.date())
#         _views_df = pd.DataFrame(views_count, index=views_created, columns=['view_count'])
#         # _views_df.index = pd.DatetimeIndex(_views_df.index)
#         # idx = pd.date_range(start, end)
#         # _views_df = _views_df.reindex(idx, fill_value=0)
#         # print(_views_df)
#         _clicks = []
#         for _view in _views:
#             _click = clicks_resample.get_click_by_view_id(
#                 db=db, view_id=_view.id)
#             for c in _click:
#                 _clicks.append(c)
#         view_count = _views_df["view_count"].sum()
#         clicks_count = []
#         clicks_created = []
#         for c in _clicks:
#             clicks_count.append(c.click_count)
#             clicks_created.append(c.click_created.date())
#         _clicks_df = pd.DataFrame(clicks_count, index=clicks_created, columns=['click_count'])
#         click_count = _clicks_df["click_count"].sum()
#         if start != None and end != None:
#             start = start.date()
#             end = end.date()
#             # add all missing dates to _views_df and _clicks_df
#             _views_df = _views_df.sort_index()
#             # print(_views_df)
#             _clicks_df = _clicks_df.sort_index()
#             # print(_views_df.to_dict())
#             _views_date_wise = _views_df.to_dict()
#             # print(_views_date_wise)
#             _clicks_date_wise = _clicks_df.to_dict()
#             print("here")
#             return JSONResponse(code=status.HTTP_200_OK, status="OK", result={"clicks": {"click_count": click_count, "click": _clicks_date_wise}, "views": {"view_count": view_count, "view": _views_date_wise}}, message="Success").dict(exclude_none=True)
        
#     except:
#         return JSONResponse(content={"message": f"Profile {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)