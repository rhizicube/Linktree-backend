from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from schemas.users import RequestUser, ResponseUser, UpdateUser
import crud.users as users

from db_connect.setup import get_db

user_router = APIRouter()


@user_router.post("/users/")
async def create(request:RequestUser, db:session=Depends(get_db)):
	"""Async function to create user

	Args:
		request (RequestUser): Serialized request data
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Profile created with 200 status if profile is created, else exception text with 400 status
	"""
	try:
		_user = users.create_user(db, request.parameter)
		return JSONResponse(content={"message": f"User {_user.username} created"}, status_code=status.HTTP_201_CREATED)
	except Exception as e:
		return ResponseUser(code=status.HTTP_400_BAD_REQUEST, status="BAD REQUEST", message=str(e)).dict(exclude_none=True)

@user_router.get("/users/")
async def get(username:str=None, db:session=Depends(get_db)):
	"""Function to get user

	Args:
		username (str, optional): username, pk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		Response: Serialized user data with 200 status if user is present, else exception text with 400 status if exception occurred, else user not found with 404 status
	"""
	try:
		if username:
			_user = users.get_user_by_username(db=db, uname=username)
			if _user:
				return ResponseUser(code=status.HTTP_200_OK, status="OK", result=_user, message="Success").dict(exclude_none=True)
			else:
				return JSONResponse(content={"message": f"User {username} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		else:
			_user = users.get_all_users(db=db)
			return ResponseUser(code=status.HTTP_200_OK, status="OK", result=_user, message="Success").dict(exclude_none=True)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@user_router.put("/users/")
async def update(request:UpdateUser, username:str=None, db:session=Depends(get_db)):
	"""Function to update user

	Args:
		request (UpdateUser): Serialized request data
		username (str, optional): Username, pk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: User updated with 200 status if user is updated, else exception text with 400 status
	"""
	try:
		_user = users.update_user(db=db, uname=username, first_name=request.parameter.first_name, last_name=request.parameter.last_name, email_id=request.parameter.email_id)
		# return ResponseUser(result=_user).dict(exclude_none=True)
		return JSONResponse(content={"message": f"User {username} updated"}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@user_router.delete("/users/")
async def delete(username:str=None, db:session=Depends(get_db)):
	"""Function to delete user

	Args:
		username (str, optional): Username, pk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: User deleted with 200 status if user is deleted, else exception text with 400 status
	"""
	try:
		if username:
			_user = users.delete_user(db=db, uname=username)
			return JSONResponse(content={"message": f"User {username} deleted"}, status_code=status.HTTP_201_CREATED)
		else:
			deleted_rows = users.delete_all_users(db)
			return JSONResponse(content={"message": f"{deleted_rows} users deleted"}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)