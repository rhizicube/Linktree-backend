import logging
import motor
import os
import motor.motor_asyncio
from .config import MONGO_DATABASE_URL
from .mongodb import db

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get(MONGO_DATABASE_URL))
db1 = client["rhizicubedb"]

# async def connect() -> motor.motor_asyncio.AsyncIOMotorClient:
#     client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get(MONGO_DATABASE_URL))
#     return client

async def connect_to_mongo():
    logging.info("Connecting to database...")
    client = motor.motor_asyncio.AsyncIOMotorClient(str(MONGO_DATABASE_URL))
    db.client = client
    logging.info("Database connected!")


async def close_mongo_connection():
    logging.info("Closing database connection...")
    db.client.close()
    logging.info("Database closed!")

