from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import session
from schemas.settings import RequestSetting, ResponseSetting, UpdateSetting
import crud.settings as settings
from PIL import Image
import io

from db_connect.setup import get_db
setting_router = APIRouter()


@setting_router.post("/setting/")
async def create(request:RequestSetting, db:session=Depends(get_db)):
    """Async function to create setting

    Args:
        request (RequestSetting): Serialized request data
        db (session, optional): DB connection session for db functionalities. Defaults to Depends(get_db).

    Returns:
        JSONResponse: Setting created with 200 status if setting is created, else exception text with 400 status
    """
    try:
        _setting = settings.create_setting(db, request.parameter)
        return JSONResponse(content={"message": f"Setting {_setting.id} created"}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@setting_router.get("/setting/")
async def get(id:int=None, profile_management:int=None, db:session=Depends(get_db)):
    try:
        if id:
            _setting = settings.get_setting_by_id(db, id)
            if _setting:
                return ResponseSetting(code=status.HTTP_200_OK, status="OK", result=_setting, message="Success").dict(exclude_none=True)
            else:
                return JSONResponse(content={"message": f"Setting {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
        elif profile_management:
            _setting = settings.get_setting_by_profile(db, profile_management)
            if _setting:
                return ResponseSetting(code=status.HTTP_200_OK, status="OK", result=_setting, message="Success").dict(exclude_none=True)
            else:
                return JSONResponse(content={"message": f"Setting {id} not found"}, status_code=status.HTTP_404_NOT_FOUND)
        else:
            _setting = settings.get_all_settings(db=db)
            return ResponseSetting(code=status.HTTP_200_OK, status="OK", result=_setting, message="Success").dict(exclude_none=True)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@setting_router.put("/setting/")
async def update(request:UpdateSetting, id:int, db:session=Depends(get_db)):
    try:
        _setting = settings.update_setting(db, id, request.parameter.profile_social)
        return JSONResponse(content={"message": f"Setting {id} updated"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@setting_router.delete("/setting/")
async def delete(id:int=None, db:session=Depends(get_db)):
    try:
        if id:
            _setting = settings.delete_setting_by_id(db, id)
            return JSONResponse(content={"message": f"Setting {id} deleted"}, status_code=status.HTTP_200_OK)
        else:
            deleted_rows = settings.delete_all_settings(db)
            return JSONResponse(content={"message": "All settings deleted"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)