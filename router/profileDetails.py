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
import os

from db_connect.setup import get_db

profile_detail_router = APIRouter()

@profile_detail_router.get("/getalldetails/")
async def get(username:str, db:session=Depends(get_db)):
	"""API to get the user's complete details

	Args:
		username (str): Username
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: User's profile, setting and link details
	"""
	try:
		# Check if the given username has profile details
		usernames = profiles.get_all_usernames(db)
		empty_user_details = {"profile": None, "link": None, "setting": None}
		if username in usernames:
			try:
				_profile = profiles.get_profile_by_user(db, username)
				if not _profile:
					return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"Profile for {username} not found", "data": empty_user_details})
			except:
				_profile = None
			if _profile is not None:
				# If profile exists, get its respective links and settings
				_links = links.get_link_by_profile(db, _profile.id)
				_settings = settings.get_setting_by_profile(db, _profile.id)
				if _settings is None:
					_settings = {}
					_profile_social = {}
				else:
					_profile_social = links.get_link_by_setting(db, _settings.id)
			else:
				return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": f"Profile for username {username} doesn't exist", "data": empty_user_details})
			# Can be converted to json format together
			resp_data = {"profile":_profile, "link":_links, "settings":_settings}
			resp_data = jsonable_encoder(resp_data)
			resp_data["settings"]["profile_social"] = jsonable_encoder(_profile_social)

			# Return profile image and link thumbnail paths from "media/"
			if resp_data["profile"]["profile_image_path"] and os.path.exists(resp_data["profile"]["profile_image_path"]):
				resp_data["profile"]["profile_image_path"] = "media" + resp_data["profile"]["profile_image_path"].split("media")[-1]
			else:
				resp_data["profile"]["profile_image_path"] = None
			for link in resp_data["link"]:
				if link["link_thumbnail"] and os.path.exists(link["link_thumbnail"]):
					link["link_thumbnail"] = "media" + link["link_thumbnail"].split("media")[-1]
				else:
					link["link_thumbnail"] = None
			for link in resp_data["settings"]["profile_social"]:
				if link["link_thumbnail"] and os.path.exists(link["link_thumbnail"]):
					link["link_thumbnail"] = "media" + link["link_thumbnail"].split("media")[-1]
				else:
					link["link_thumbnail"] = None
			# "empty_profile" added to identify user hasnt updated details other than their profile image, so remove it in the response
			if "empty_profile" in resp_data["profile"]["profile_link"]:
				resp_data["profile"]["profile_link"] = ""
			if "empty_profile" in resp_data["profile"]["profile_name"]:
				resp_data["profile"]["profile_name"] = ""
			return JSONResponse(status_code=status.HTTP_200_OK, content={"data": resp_data})
		else:
			return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": f"Profile for username {username} doesn't exist", "data": empty_user_details})
	except Exception as e:
		return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":str(e)})


@profile_detail_router.post("/savedetails/")
async def create(username:str, request: Dict[Any, Any], db:session=Depends(get_db)):
	"""API to create user's details

	Args:
		username (str): username
		request (Dict[Any, Any]): Request body
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: User's profile details created with 201 status if detail is created, else exception text with 400 status
	"""
	try:
		if username:
			response_data = {} # To return back the primary key details for the created rows
			# Check if the given username has profile details
			all_usernames = profiles.get_all_usernames(db)
			# If profile exists, get profile. Else, get profile details from request and create profile
			if username in all_usernames or request.get("profile", None) is None:
				_profile = profiles.get_profile_by_user(db, username)
				if not _profile:
					return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"Profile for {username} not found"})
			else:
				request["profile"]["username"] = username
				profile = ProfileSchema(**request["profile"])
				_profile = profiles.create_profile(db, profile)
				print(profile)
				response_data["profile"] = jsonable_encoder(_profile)
				# Return profile image path from "media/"
				if response_data["profile"]["profile_image_path"] and os.path.exists(response_data["profile"]["profile_image_path"]):
					response_data["profile"]["profile_image_path"] = "media" + response_data["profile"]["profile_image_path"].split("media")[-1]

			# Create setting if present in request body
			if request.get("setting", None) is not None:
				request["setting"]["profile"] = _profile.id
				setting = SettingSchema(**request["setting"])
				_setting = settings.create_setting(db, setting)
				response_data["setting"] = jsonable_encoder(_setting)
			else:
				_setting = settings.get_setting_by_profile(db, _profile.id)
				if not _setting:
					request["setting"] = {"profile": _profile.id}
					setting = SettingSchema(**request["setting"])
					_setting = settings.create_setting(db, setting)
					response_data["setting"] = jsonable_encoder(_setting)

			# Create link if present in request body
			if request.get("link", None) is not None:
				link = request["link"]
				link["profile"] = _profile.id
				link = LinkSchema(**link)
				_link = links.create_link(db, link)
				response_data["links"] = jsonable_encoder(_link)
				if response_data["links"]["link_thumbnail"]:
					response_data["links"]["link_thumbnail"] = "media" + response_data["links"]["link_thumbnail"].split("media")[-1]
			# Create profile_social if present in request body
			if request.get("profile_social", None) is not None:
				link = request["profile_social"]
				link["setting"] = _setting.id
				link = LinkSchema(**link)
				_link = links.create_link(db, link)
				if "setting" not in response_data.keys():
					response_data["setting"] = jsonable_encoder(_setting)
				response_data["setting"]["profile_social"] = jsonable_encoder(_link)
				if response_data["setting"]["profile_social"]["link_thumbnail"]:
					response_data["setting"]["profile_social"]["link_thumbnail"] = "media" + response_data["setting"]["profile_social"]["link_thumbnail"].split("media")[-1]

			# Response to contain the rows inserted to DB (to include primary keys)
			return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message":"Profile details saved", "data": response_data})
		else:
			return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"Username is required"})
	except Exception as e:
		return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":str(e)})


@profile_detail_router.put("/updatedetails/")
async def update(username:str, request: Dict[Any, Any], link_id:int=None, db:session=Depends(get_db)):
	"""API to update user's details

	Args:
		username (str): Username
		request (Dict[Any, Any]): Request body
		link_id (int, optional): Link id, pk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Profile details updated with 200 status if profile/setting/link is updated, else exception text with 400 status
	"""
	try:
		if username:
			# Get profile for username
			profile = profiles.get_profile_by_user(db, username)
			if not profile:
				return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"Profile for {username} not found"})

			# If profile is to be updated
			if request.get("profile", None) is not None:
				_profile = profiles.update_profile(db, profile.id, request["profile"].get("profile_bio", None), request["profile"].get("profile_name", None), request["profile"].get("profile_link", None))
			if request.get("setting", None) is not None:
				setting = settings.get_setting_by_profile(db, profile.id)
				_setting = settings.update_setting(db, setting.id, request["setting"].get("profile_social", None))
			# If a link is to be updated
			if link_id is not None and (request.get("link", None) is not None or request.get("profile_social", None) is not None):
				link_request = request["link"] if request.get("link", None) is not None else request["profile_social"] 
				_link = links.update_link(db, link_id, link_request.get("link_enable", None), link_request.get("link_name", None), link_request.get("link_url", None), link_request.get("link_thumbnail", None))
			return JSONResponse(status_code=status.HTTP_200_OK, content={"message":"Profile details updated"})
		else:
			return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"Username is required"})
	except Exception as e:
		return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":str(e)})
