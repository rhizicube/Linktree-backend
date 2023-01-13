import os
import motor.motor_asyncio
from models import Views, UpdateViews
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Body, HTTPException, status
from typing import List
from config import MONGO_DATABASE_URL
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get(MONGO_DATABASE_URL))
db1 = client["rhizicubedb"]
view_mongo_router = APIRouter()
@view_mongo_router.post("/", response_description="Add new view", response_model=Views)
async def create_view(view: Views = Body(...)):
    view = jsonable_encoder(view)
    new_view = await db1["views"].insert_one(view)
    created_view = await db1["views"].find_one({"_id": new_view.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_view)

@view_mongo_router.get('/views')
async def list_views(id: str=None):
    if id is not None:
        if (view := await db1["views"].find_one({"_id": id})) is not None:
            return view
        raise HTTPException(status_code=404, detail=f"Student {id} not found")
    else:
        views = await db1["views"].find().to_list(1000)
        return {'views': views}

