from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from schemas.views_resample import RequestView, ResponseView, UpdateView
import crud.views_resample as views_resample
from db_connect.setup import get_db

view_router = APIRouter()


@view_router.post("/views/")
async def create(request:RequestView, db:session=Depends(get_db)):
	try:
		_view = views_resample.create_view(db, request.parameter)
		return JSONResponse(content={"message": f"View {_view.id} created"}, status_code=status.HTTP_201_CREATED)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@view_router.get("/view/")
async def get(id:int=None, db:session=Depends(get_db)):
	try:
		if id:
			_view = views_resample.get_view_by_id(db, id)
			if _view:
				return ResponseView(code=status.HTTP_200_OK, status="OK", result=_view, message="Success").dict(exclude_none=True)
			else:
				return JSONResponse(content={"message": f"View {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		else:
			_view = views_resample.get_all_views(db=db)
			return ResponseView(code=status.HTTP_200_OK, status="OK", result=_view, message="Success").dict(exclude_none=True)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@view_router.put("/view/")
async def update(request:UpdateView, id:int=None, db:session=Depends(get_db)):
	if id:
        try:
            view_id = views_resample.get_view_by_id(db, id)
            if view_id is not None:
                _view = views_resample.update_view(db, request.parameter, id)
                return JSONResponse(content={"message": f"View {id} updated"}, status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content={"message": f"View {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@view_router.delete("/view/")
async def delete(id:int=None, db:session=Depends(get_db)):
	try:
		if id:
			_view = views_resample.delete_view(db, id)
			return JSONResponse(content={"message": f"View {id} deleted"}, status_code=status.HTTP_200_OK)
		else:
			deleted_rows = views_resample.delete_all_views(db)
			return JSONResponse(content={"message": f"Views deleted"}, status_code=status.HTTP_200_OK)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
