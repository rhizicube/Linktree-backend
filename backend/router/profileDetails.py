from fastapi import APIRouter, Depends, status
from typing import Any, Dict
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
import crud.profiles as profiles
import crud.links as links
import crud.settings as settings
from fastapi.encoders import jsonable_encoder
from schemas.links import LinkSchema
from schemas.settings import SettingSchema
from schemas.profiles import ProfileSchema
import json

from setup import get_db

profile_detail_router = APIRouter()

@profile_detail_router.get("/getalldetails")
async def get(username:str, db:session=Depends(get_db)):
    # proceed if username exists
    try:
        if username:
            try:
                _profile = profiles.get_profile_by_user(db, username)
            except:
                _profile = None
            if _profile is not None:
                _links = links.get_link_by_profile(db, _profile.id)
                _settings = settings.get_setting_by_profile(db, _profile.id)
            else:
                _links = None
                _settings = None
            _profile_json = jsonable_encoder(_profile)
            _links_json = jsonable_encoder(_links)
            _settings_json = jsonable_encoder(_settings)
            return JSONResponse(status_code=status.HTTP_200_OK, content={"data":{"profile":_profile_json, "link":_links_json, "settings":_settings_json}})
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"Username is required"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":str(e)})

# @profile_detail_router.post("/savedetails/")
# async def create(username:str, request: Dict[Any, Any], db:session=Depends(get_db)):
    # return {
    #     "status" : "SUCCESS",
    #     "data" : request
    # }
#     # request = await request.json()
    # try:
    #     if username:
    #         if request["profile"] is not None:
    #             request["profile"]["username"] = username
    #             profile = ProfileSchema(**request["profile"])
    #             _profile = profiles.create_profile(db, profile)
    #             print(profile)
    #         if request["link"] is not None:
    #             for link in request["link"]:
    #                 link["profile_id"] = _profile.id
    #                 link["tiny_url"] = ""
    #                 link = LinkSchema(**link)
    #                 _link = links.create_link(db, link)
    #                 profile(link)
    #         if request["settings"] is not None:
    #             request["settings"]["profile_management"] = _profile.id
    #             setting = SettingSchema(**request["setting"])
    #             _setting = settings.create_setting(db, setting)
    #             print(setting)
    #         return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message":"Profile details saved"})
    #     else:
    #         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"Username is required"})
    # except Exception as e:
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":str(e)})

# @profile_detail_router.post("/savedetails/")
# async def create(username:str, request: Dict[Any, Any], db:session=Depends(get_db)):
#     return {
#         "status" : "SUCCESS",
#         "data" : request
#     }