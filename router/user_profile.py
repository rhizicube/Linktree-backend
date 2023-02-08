from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import session
import crud.profiles as profiles, crud.links as links, crud.settings as settings, crud.views as views, crud.clicks as clicks
# from utilities.views import create_cookie_id, get_client_details
from fastapi.encoders import jsonable_encoder


from db_connect.setup import get_db

router = APIRouter()


async def get_user_profile_details(url:str, request:Request, db:session):
	"""Function to get profile details

	Args:
		url (str): User's unique custom link
		db (session): DB connection session for db functionalities

	Returns:
		nested dict: Containing profile, link and setting information
	"""
	response_cookie = None
	# If cookie isn't present in the browser, create and set one
	# cookie_id = request.cookies.get('linktree_visitor', None)
	# if not cookie_id:
		# cookie_id = await create_cookie_id()
		# response_cookie = cookie_id
	# Get user's profile configurations
	_profile = profiles.get_profile_by_url(db, url)
	if not _profile:
		return {"profile": None, "link": None, "setting": None}, response_cookie
	_link = links.get_link_by_profile(db, _profile.id)
	_setting = settings.get_setting_by_profile(db, _profile.id)
	resp_data = {"profile": _profile, "link": _link, "setting": _setting}
	# Save view information
	# device, location = get_client_details(request)
	# await views.create_view_raw(cookie_id, device, location, _profile.id)
	return resp_data, response_cookie


async def save_click(link:str, request:Request):
	"""Function to save click information

	Args:
		link (str): Link clicked on
		request (Request): API request

	Returns:
		str: If browser cookie is expired, a new cookie is created and set
		None: If browser cookie is still active
	"""
	# If cookie isn't present in the browser, create and set one
	response_cookie = None
	session_id = request.cookies.get('linktree_visitor', None)
	# if not session_id:
		# session_id = await create_cookie_id()
		# response_cookie = session_id
	# Save click information
	# await clicks.create_click_raw(session_id, link)
	return response_cookie



"""Examples

For short link: http://localhost:8000/8UXFZKEDAF
For custom linktree url: http://localhost:8000/user2
"""
@router.get("/{url}")
async def get_user_profile(url:str, request:Request, db:session=Depends(get_db)):
	"""API to get user's profile details or redirect to user's social websites based on given input URL

	Args:
		url (str): Short link or custom linktree's custom link
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		ResponseProfile (optional): Response containing Profile, setting and link details for user
		RedirectResponse (optional): Redirect tiny link to the original link provided by user
	"""
	try:
		all_short_links = links.get_all_tiny_links(db) # To check if the given URL is a tiny link or custom url
		if url in all_short_links:
			# given URL is a tiny/shortened link. API needs to redirect to the original link to which the tiny link is pointed to
			link_to_redirect = links.get_link_by_tiny_url(url, db)
			response_cookie = await save_click(url, request)
			response = RedirectResponse(link_to_redirect)
			if response_cookie:
				response.set_cookie(key="linktree_visitor", value=response_cookie, expires=100)
			return response
		else:
			# given URL is a custom link. All profile details (profile, links, settings) linked to the custom link is sent back as response
			resp_data, response_cookie = await get_user_profile_details(url, request, db)
			resp_data = jsonable_encoder(resp_data)
			if "empty" in resp_data["profile"]["profile_name"]:
				resp_data["profile"]["profile_name"] = ""
			response = JSONResponse(content={"data": resp_data}, status_code=status.HTTP_200_OK)
			if response_cookie:
				response.set_cookie(key="linktree_visitor", value=response_cookie, expires=100)
			return response
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
