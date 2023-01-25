from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from schemas.clicks_resample import RequestClick, ResponseClick, UpdateClick
import crud.clicks_resample as clicks_resample


from db_connect.setup import get_db

click_router = APIRouter()


@click_router.post("/click/")
async def create(request:RequestClick, db:session=Depends(get_db)):
	"""Async function to create click

	Args:
		request (RequestClick): Serialized request data
		db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

	Returns:
		JSONResponse: Click created with 200 status if click is created, else exception text with 400 status
	"""
	try:
		_click = clicks_resample.create_click(db, request.parameter)
		return JSONResponse(content={"message": f"Click {_click.id} created"}, status_code=status.HTTP_201_CREATED)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@click_router.get("/click/")
async def get(id:int=None, link_id:int=None, view_id:int=None, db:session=Depends(get_db)):
	try:
		if id:
			_click = clicks_resample.get_click_by_id(db=db, id=id)
			if _click:
				return ResponseClick(code=status.HTTP_200_OK, status="OK", result=_click, message="Success").dict(exclude_none=True)
			else:
				return JSONResponse(content={"message": f"Click {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		elif link_id:
			_click = clicks_resample.get_click_by_link_id(db=db, link_id=link_id)
			if _click:
				return ResponseClick(code=status.HTTP_200_OK, status="OK", result=_click, message="Success").dict(exclude_none=True)
			else:
				return JSONResponse(content={"message": f"Click {link_id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		elif view_id:
			_click = clicks_resample.get_click_by_view_id(db=db, view_id=view_id)
			if _click:
				return ResponseClick(code=status.HTTP_200_OK, status="OK", result=_click, message="Success").dict(exclude_none=True)
			else:
				return JSONResponse(content={"message": f"Click {view_id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
		else:
			_click = clicks_resample.get_all_clicks(db=db)
			return ResponseClick(code=status.HTTP_200_OK, status="OK", result=_click, message="Success").dict(exclude_none=True)
	except Exception as e:
		return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@click_router.put("/click/")
try:
        click_id = clicks_resample.get_click_by_id(db=db, id=id)
        if click_id is not None:
            _click = clicks_resample.update_click(db=db, id=id, request=request)
            return JSONResponse(content={"message": f"Click {id} updated"}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={"message": f"Click {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@click_router.delete("/click/")
async def delete(id:int=None, db:session=Depends(get_db)):
	try:
        if id:
            click_id = clicks_resample.get_click_by_id(db=db, id=id)
            if click_id is not None:
                _click = clicks_resample.delete_click_by_id(db=db, id=id)
                return JSONResponse(content={"message": f"Click {id} deleted"}, status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content={"message": f"Click {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
        else:
            deleted_rows = clicks_resample.delete_all_clicks(db=db)
            return JSONResponse(content={"message": f"Clicks deleted"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)
