import os
import motor.motor_asyncio
from models import Views, UpdateViews
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Body, HTTPException, status
from typing import List
from db_connect.config import MONGO_DATABASE_URL
import db_connect.mongodb as mongodb
from db_connect.mongodb_utils import client
from core.settings import settings
db1 = client[settings.MONGO_DB_NAME]
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


@view_mongo_router.put("/{id}", response_description="Update a view", response_model=Views)
async def update_view(id: str, view: UpdateViews = Body(...)):
    view = {k: v for k, v in view.dict().items() if v is not None}

    if len(view) >= 1:
        update_result = await db1["views"].update_one({"_id": id}, {"$set": view})

        if update_result.modified_count == 1:
            if (
                updated_view := await db1["views"].find_one({"_id": id})
            ) is not None:
                return updated_view

    if (existing_view := await db1["views"].find_one({"_id": id})) is not None:
        return existing_view

    raise HTTPException(status_code=404, detail=f"View {id} not found")


@view_mongo_router.delete("/{id}", response_description="Delete a view")
async def delete_view(id: str):
    if (existing_view := await db1["views"].find_one({"_id": id})) is not None:
        delete_result = await db1["views"].delete_one({"_id": id})
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="View deleted")
    raise HTTPException(status_code=404, detail=f"View {id} not found")