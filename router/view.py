from fastapi import Body, status, APIRouter
from fastapi.responses import JSONResponse
from schemas.models import UpdateViews
import crud.views as views
import json
from bson import json_util
from bson.objectid import ObjectId

view_router= APIRouter()


@view_router.post("/view/")
async def create_view(view: UpdateViews = Body(...)):
	"""API to create view

	Args:
		request (UpdateViews): Serialized request data

	Returns:
		JSONResponse: View created with 201 status if view is created, else exception text with 400 status
	"""
	try:
		_view = await views.create_view_raw(view['session_id'], view['device'], view['location'], view['profile_link'])
		res = json.loads(json_util.dumps(_view))
		return JSONResponse(status_code=status.HTTP_201_CREATED, content=res)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@view_router.get("/view/")
async def get_view(id: str = None, profile:int = None):
	"""API to get views

	Args:
		id (str, optional): View id, pk. Defaults to None.

	Returns:
		JSONResponse: Serialized views data with 200 status if view is present, else exception text with 400 status if exception occurred, else view not found with 404 status
	"""
	try:
		if id:
			_view = await views.get_view_by_id(ObjectId(id))
		elif profile:
			_view = await views.get_views_by_profile(profile)
		else:
			_view = await views.get_all_views()
		if not _view:
			return JSONResponse(content={"message": "View record not found"}, status_code=status.HTTP_404_NOT_FOUND)
		res = json.loads(json_util.dumps(_view))
		return JSONResponse(status_code=status.HTTP_200_OK, content=res)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@view_router.delete("/view/")
async def delete_view(id: str = None):
	"""API to delete view

	Args:
		id (str, optional): View id, pk. Defaults to None.

	Returns:
		JSONResponse: View deleted with 200 status if view is deleted, else exception text with 400 status
	"""
	try:
		if id:
			_view = await views.delete_view_by_id(ObjectId(id))
		else:
			_view = await views.delete_all_views()
		return JSONResponse(status_code=status.HTTP_200_OK, content={"deleted_rows": _view.deleted_count})
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
