from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from schemas.links import RequestLink, ResponseLink, UpdateLink
import crud.links as links
from PIL import Image
import io


from setup import get_db

link_router = APIRouter()


@link_router.post("/link/")
async def create(request:RequestLink, db:session=Depends(get_db)):
	"""Async function to create link

	Args:
		request (RequestLink): Serialized request data
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Link created with 200 status if link is created, else exception text with 400 status
	"""
	try:
		_link = links.create_link(db, request.parameter)
		return JSONResponse(content={"message": f"Link {_link.id} created"}, status_code=status.HTTP_201_CREATED)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@link_router.get("/link/")
async def get(id:int=None, profile_id:int=None, db:session=Depends(get_db)):
	"""Async function to get link

	Args:
		id (int, optional): Link id, pk. Defaults to None.
		profile_id (int, optional): Profile id, fk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		Response: Serialized link data with 200 status if link is present, else exception text with 400 status if exception occurred, else link not found with 404 status
	"""
	try:
		if id:
			_link = links.get_link_by_id(db, id)
			if _link:
				return ResponseLink(code=status.HTTP_200_OK, status="OK", result=_link, message="Success").dict(exclude_none=True)
			else:
				return JSONResponse(content={"message": f"Link {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		elif profile_id:
			_link = links.get_link_by_user(db, profile_id)
			if _link:
				return ResponseLink(code=status.HTTP_200_OK, status="OK", result=_link, message="Success").dict(exclude_none=True)
			else:
				return JSONResponse(content={"message": f"Link {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		else:
			_link = links.get_all_links(db=db)
			return ResponseLink(code=status.HTTP_200_OK, status="OK", result=_link, message="Success").dict(exclude_none=True)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@link_router.put("/link/")
async def update(request:UpdateLink, id:int=None, db:session=Depends(get_db)):
	"""Async function to update link

	Args:
		request (UpdateLink): Serialized request data
		id (int, optional): Link id, pk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Link updated with 200 status if link is updated, else exception text with 400 status
	"""
	try:
		_link = links.update_link(db, id, request.parameter.link_bio)
		return JSONResponse(content={"message": f"Link {id} updated"}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@link_router.delete("/link/")
async def delete(id:int=None, db:session=Depends(get_db)):
	"""Async function to delete link

	Args:
		id (int, optional): link id, pk. Defaults to None.
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Link deleted with 200 status if link is deleted, else exception text with 400 status
	"""
	try:
		if id:
			_link = links.delete_link_by_id(db, id)
			return JSONResponse(content={"message": f"Link {id} deleted"}, status_code=status.HTTP_200_OK)
		else:
			deleted_rows = links.delete_all_links(db)
			return JSONResponse(content={"message": f"{deleted_rows} links deleted"}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@link_router.put("/link/image/")
async def update_image(file:UploadFile=File(...), id:int=None, db:session=Depends(get_db)):
	try:
		_link = links.update_link_image(db, id, file)
		return JSONResponse(content={"message": f"Link {id} updated"}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
