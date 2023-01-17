from fastapi import status, APIRouter
from fastapi.responses import JSONResponse
import crud.clicks as clicks
import json
from bson import json_util
from schemas.models import UpdateClicks
from bson.objectid import ObjectId

click_router= APIRouter()


@click_router.get("/click/")
async def get_click(id: str = None):
	"""API to get clicks

	Args:
		id (str, optional): Click id, pk. Defaults to None.

	Returns:
		JSONResponse: Serialized clicks data with 200 status if click is present, else exception text with 400 status if exception occurred, else link not found with 404 status
	"""
	try:
		if id:
			_click = await clicks.get_click_by_id(ObjectId(id))
		else:
			_click = await clicks.get_all_clicks()
		if not _click:
			return JSONResponse(content={"message": "View record not found"}, status_code=status.HTTP_404_NOT_FOUND)
		res = json.loads(json_util.dumps(_click))
		return JSONResponse(status_code=status.HTTP_200_OK, content=res)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@click_router.delete("/click/")
async def delete_click(id: str = None):
	"""API to delete click

	Args:
		id (str, optional): Click id, pk. Defaults to None.

	Returns:
		JSONResponse: Click deleted with 200 status if click is deleted, else exception text with 400 status
	"""
	try:
		if id:
			_click = await clicks.delete_click_by_id(ObjectId(id))
		else:
			_click = await clicks.delete_all_clicks()
		return JSONResponse(status_code=status.HTTP_200_OK, content={"deleted_rows": _click.deleted_count})
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@click_router.post("/click/")
async def create_click(request:UpdateClicks):
	"""API to create link

	Args:
		request (UpdateClicks): Serialized request data

	Returns:
		JSONResponse: Click created with 201 status if link is created, else exception text with 400 status
	"""
	try:
		_click = await clicks.create_click_raw(request.session_id, request.link)
		return JSONResponse(content={"message": f"Click {_click['_id']} created"}, status_code=status.HTTP_201_CREATED)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
