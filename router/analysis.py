from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from schemas.clicks_resample import RequestClick, ResponseClick, UpdateClick
import crud.clicks_resample as clicks_resample
import crud.views_resample as views_resample
from crud.profiles import get_profile_by_id
from db_connect.setup import get_db
from datetime import datetime as dt
analysis_router = APIRouter()


# return count of all clicks and views gor a profile
@analysis_router.get("/analysis/")
async def get(id:int, start:dt=None, end:dt=None, db:session=Depends(get_db)):
    if start==None and end==None:
        try:
            _profile = get_profile_by_id(db=db, id=id)
            if _profile is not None:
                _views = views_resample.get_views_by_profile_id(db=db, profile_id=id)
                _clicks=[]
                for _view in _views:
                    _click = clicks_resample.get_click_by_view_id(db=db, view_id=_view.id)
                    _clicks.append(_click)
                # return number of clicks date-wise

                return ResponseClick(code=status.HTTP_200_OK, status="OK", result={"clicks": {"click_count":len(_clicks)}, "views": {"view_count":len(_views)}}, message="Success").dict(exclude_none=True)
            else:
                return JSONResponse(content={"message": f"Profile {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
    elif start!=None and end!=None:
        start = start.date()
        end = end.date()
        try:
            _profile = get_profile_by_id(db=db, id=id)
            if _profile is not None:
                _views = views_resample.get_views_by_profile_id(db=db, profile_id=id)
                _clicks = clicks_resample.get_click_by_view_id(db=db, view_id=_views[0].id)
                # save number of clicks date-wise from start to end in dict
                _clicks_date_wise = {}
                for _click in _clicks:
                    if start <= _click.click_created.date() and start <= _click.click_created.date():
                        if start <= _click.click_created.date() and start <= _click.click_created.date() and _click.click_created.date() in _clicks_date_wise:
                            _clicks_date_wise[_click.click_created.date()] += 1
                        else:
                            _clicks_date_wise[_click.click_created.date()] = 1
                        return ResponseClick(code=status.HTTP_200_OK, status="OK", result={"clicks": {"click_count":len(_clicks), "click":_clicks_date_wise}, "views": {"view_count":len(_views)}}, message="Success").dict(exclude_none=True)
            else:
                return JSONResponse(content={"message": f"Profile {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
    




