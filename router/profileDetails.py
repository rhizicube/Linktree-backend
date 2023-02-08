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

from db_connect.setup import get_db

profile_detail_router = APIRouter()

@profile_detail_router.get("/getalldetails/")
async def get(username:str, db:session=Depends(get_db)):
	# proceed if username exists
	try:
		usernames = profiles.get_all_usernames(db)
		if username in usernames:
			try:
				_profile = profiles.get_profile_by_user(db, username)
			except:
				_profile = None
			if _profile is not None:
				_links = links.get_link_by_profile(db, _profile.id)
				_settings = settings.get_setting_by_profile(db, _profile.id)
			else:
				return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"Profile doesn't exist"})
			# Can be converted to json format together
			resp_data = {"profile":_profile, "link":_links, "settings":_settings}
			resp_data = jsonable_encoder(resp_data)
			# if profile_link has "empty_profile" in it, remove it
			if "empty" in resp_data["profile"]["profile_link"]:
				resp_data["profile"]["profile_link"] = ""
			if "empty" in resp_data["profile"]["profile_name"][:13]:
				resp_data["profile"]["profile_name"] = ""
			return JSONResponse(status_code=status.HTTP_200_OK, content={"data": resp_data})
		else:
			return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"Username is required"})
	except Exception as e:
		return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":str(e)})


@profile_detail_router.post("/savedetails/")
async def create(username:str, request: Dict[Any, Any], db:session=Depends(get_db)):
	try:
		if username:
			response_data = {} # To return back the primary key details for the created rows
			# If profile isnt there in request, get _profile separately
			all_usernames = profiles.get_all_usernames(db)
			if username in all_usernames or request.get("profile", None) is None:
				_profile = profiles.get_profile_by_user(db, username)
			else:
				request["profile"]["username"] = username
				profile = ProfileSchema(**request["profile"])
				_profile = profiles.create_profile(db, profile)
				print(profile)
				response_data["profile"] = jsonable_encoder(_profile)
			if request.get("link", None) is not None:
				if type(request["link"]) == list:
					resp_links = []
					for link in request["link"]:
						link["profile"] = _profile.id
						link = LinkSchema(**link)
						_link = links.create_link(db, link)
						print(link)
						resp_links.append(jsonable_encoder(_link))
					response_data["links"] = resp_links
				else:
					link = request["link"]
					link["profile"] = _profile.id
					link = LinkSchema(**link)
					_link = links.create_link(db, link)
					print(link)
					response_data["links"] = jsonable_encoder(_link)
			if request.get("setting", None) is not None:
				request["setting"]["profile"] = _profile.id
				setting = SettingSchema(**request["setting"])
				_setting = settings.create_setting(db, setting)
				print(setting)
				response_data["setting"] = jsonable_encoder(_setting)
			return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message":"Profile details saved", "data": response_data})
		else:
			return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"Username is required"})
	except Exception as e:
		return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":str(e)})


@profile_detail_router.put("/updatedetails/")
async def update(username:str, request: Dict[Any, Any], link_id:int=None, db:session=Depends(get_db)):
	try:
		if username:
			profile = profiles.get_profile_by_user(db, username)
			if request.get("profile", None) is not None:
				_profile = profiles.update_profile(db, profile.id, request["profile"].get("profile_bio", None), request["profile"].get("profile_name", None), request["profile"].get("profile_link", None))
			if request.get("setting", None) is not None:
				setting = settings.get_setting_by_profile(db, profile.id)
				_setting = settings.update_setting(db, setting.id, request["setting"].get("profile_social", None))
			if link_id is not None and request.get("link", None) is not None and type(request["link"]) == dict:
				_link = links.update_link(db, link_id, request["link"].get("link_enable", None), request["link"].get("link_name", None), request["link"].get("link_url", None))
			return JSONResponse(status_code=status.HTTP_200_OK, content={"message":"Profile details updated"})
		else:
			return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"Username is required"})
	except Exception as e:
		return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":str(e)})
