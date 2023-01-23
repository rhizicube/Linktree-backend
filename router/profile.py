from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from schemas.profiles import RequestProfile, ResponseProfile, UpdateProfile
import crud.profiles as profiles


from db_connect.setup import get_db

profile_router = APIRouter()


# @profile_router.post("/profile/")
async def create(request:RequestProfile, db:session=Depends(get_db)):
	"""API to create profile

	Args:
		request (RequestProfile): Serialized request data
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Profile created with 200 status if profile is created, else exception text with 400 status
	"""
	try:
		_profile = profiles.create_profile(db, request.parameter)
		return JSONResponse(content={"message": f"Profile {_profile.id} created"}, status_code=status.HTTP_201_CREATED)
	except Exception as e:
		if "(psycopg2.errors.UniqueViolation)" in str(e):
			return JSONResponse(content={"message": f"Profile Link already exists"}, status_code=status.HTTP_400_BAD_REQUEST)
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@profile_router.get("/profile/")
async def get(id:int=None, username:str=None, db:session=Depends(get_db)):
	"""API to get profile

	Args:
		id (int, optional): Profile id, pk. Defaults to None.
		username (str, optional): Username, fk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		Response: Serialized profile data with 200 status if profile is present, else exception text with 400 status if exception occurred, else profile not found with 404 status
	"""
	try:
		if id:
			_profile = profiles.get_profile_by_id(db, id)
			if _profile:
				return ResponseProfile(code=status.HTTP_200_OK, status="OK", result=_profile, message="Success").dict(exclude_none=True)
			else:
				return JSONResponse(content={"message": f"Profile {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		elif username:
			_profile = profiles.get_profile_by_user(db, username)
			if _profile:
				return ResponseProfile(code=status.HTTP_200_OK, status="OK", result=_profile, message="Success").dict(exclude_none=True)
			else:
				return JSONResponse(content={"message": f"Profile {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		else:
			_profile = profiles.get_all_profiles(db=db)
			return ResponseProfile(code=status.HTTP_200_OK, status="OK", result=_profile, message="Success").dict(exclude_none=True)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


# @profile_router.put("/profile/")
async def update(request:UpdateProfile, id:int=None, db:session=Depends(get_db)):
	"""API to update profile

	Args:
		request (UpdateProfile): Serialized request data
		id (int, optional): Profile id, pk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Profile updated with 200 status if profile is updated, else exception text with 400 status
	"""
	try:
		_profile = profiles.update_profile(db, id, request.parameter.profile_bio, request.parameter.profile_name, request.parameter.profile_link)
		return JSONResponse(content={"message": f"Profile {id} updated"}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@profile_router.delete("/profile/")
async def delete(id:int=None, db:session=Depends(get_db)):
	"""API to delete profile

	Args:
		id (int, optional): profile id, pk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Profile deleted with 200 status if profile is deleted, else exception text with 400 status
	"""
	try:
		if id:
			_profile = profiles.delete_profile_by_id(db, id)
			return JSONResponse(content={"message": f"Profile {id} deleted"}, status_code=status.HTTP_200_OK)
		else:
			deleted_rows = profiles.delete_all_profiles(db)
			return JSONResponse(content={"message": f"{deleted_rows} profiles deleted"}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@profile_router.put("/profile/image/")
async def update_image(file:UploadFile=File(...), id:int=None, db:session=Depends(get_db)):
	"""API to update profile image

	Args:
		file (UploadFile, optional): Uploaded image. Defaults to File(...).
		id (int, optional): profile id, pk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Profile updated with 200 status if profile is updated, else exception text with 400 status
	"""
	try:
		_profile = profiles.update_profile_image(db, id, file)
		return JSONResponse(content={"message": f"Profile {id} updated"}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
