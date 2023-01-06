from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import session
from schemas.profiles import ResponseProfile
import crud.profiles as profiles, crud.links as links, crud.settings as settings


from db_connect.setup import get_db

router = APIRouter()


def get_user_profile_details(url:str, db:session):
	"""Function to get profile details

	Args:
		url (str): User's unique custom link
		db (session): DB connection session for db functionalities

	Returns:
		nested dict: Containing profile, link and setting information
	"""
	_profile = profiles.get_profile_by_url(db, url)
	_link = links.get_link_by_profile(db, _profile.id)
	_setting = settings.get_setting_by_profile(db, _profile.id)
	resp_data = {"profile": _profile, "link": _link, "setting": _setting}
	return resp_data




"""Examples

For short link: http://localhost:8000/8UXFZKEDAF
For custom linktree url: http://localhost:8000/user2
"""
@router.get("/{url}")
async def get_user_profile(url:str, db:session=Depends(get_db)):
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
			link_to_redirect = links.get_profile_by_tiny_link(url, db)
			return RedirectResponse(link_to_redirect)
		else:
			# given URL is a custom link. All profile details (profile, links, settings) linked to the custom link is sent back as response
			resp_data = get_user_profile_details(url, db)
			return ResponseProfile(code=status.HTTP_200_OK, status="OK", result=resp_data, message="Success").dict(exclude_none=True)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

