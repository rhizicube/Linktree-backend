import logging

from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DATABASE_URL
from .mongodb import db


async def connect_to_mongo():
    logging.info("Connecting to database...")
    db.client = AsyncIOMotorClient(str(MONGO_DATABASE_URL))
    logging.info("Database connected！")


async def close_mongo_connection():
    logging.info("Closing database connection...")
    db.client.close()
    logging.info("Database closed！")

