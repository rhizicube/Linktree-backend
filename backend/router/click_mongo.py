import os
import motor.motor_asyncio
from models import Clicks, UpdateClicks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Body, HTTPException, status
from typing import List
from db_connect.config import MONGO_DATABASE_URL
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get(MONGO_DATABASE_URL))
db1 = client["rhizicubedb"]
click_mongo_router = APIRouter()
@click_mongo_router.post("/", response_description="Add new click", response_model=Clicks)
async def create_click(click: Clicks = Body(...)):
    click = jsonable_encoder(click)
    new_click = await db1["Clicks"].insert_one(click)
    created_click = await db1["Clicks"].find_one({"_id": new_click.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_click)

@click_mongo_router.get('/clicks')
async def list_Clicks(id: str=None):
    if id is not None:
        if (click := await db1["Clicks"].find_one({"_id": id})) is not None:
            return click
        raise HTTPException(status_code=404, detail=f"Click {id} not found")
    else:
        Clicks = await db1["Clicks"].find().to_list(1000)
        return {'Clicks': Clicks}


@click_mongo_router.put("/{id}", response_description="Update a click", response_model=Clicks)
async def update_click(id: str, click: UpdateClicks = Body(...)):
    click = {k: v for k, v in click.dict().items() if v is not None}

    if len(click) >= 1:
        update_result = await db1["Clicks"].update_one({"_id": id}, {"$set": click})

        if update_result.modified_count == 1:
            if (
                updated_click := await db1["Clicks"].find_one({"_id": id})
            ) is not None:
                return updated_click

    if (existing_click := await db1["Clicks"].find_one({"_id": id})) is not None:
        return existing_click

    raise HTTPException(status_code=404, detail=f"Click {id} not found")


@click_mongo_router.delete("/{id}", response_description="Delete a click")
async def delete_click(id: str):
    if (existing_click := await db1["Clicks"].find_one({"_id": id})) is not None:
        delete_result = await db1["Clicks"].delete_one({"_id": id})
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content="Click deleted")
    raise HTTPException(status_code=404, detail=f"Click {id} not found")

# @click_mongo_router.get("/{id}", response_description="Get a single click", response_model=Clicks)
# async def show_click(id: str):
#     if (click := await db1["Clicks"].find_one({"_id": id})) is not None:
#         return click
#     raise HTTPException(status_code=404, detail=f"Click {id} not found")