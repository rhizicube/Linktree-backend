from .config import postgre_sessionLocal, mongoDB, MONGO_DATABASE_URL
import motor.motor_asyncio
from core.settings import settings


"""Connect to PostgreSQL DB and create session, and begin transaction"""

def get_db():
	db = postgre_sessionLocal()
	db.begin()
	try:
		yield db
	finally:
		db.close()

get_db()



"""Connect to Mongo DB and create session, and begin transaction"""

async def connect_to_mongo():
	print("Connecting to MongoDB...")
	mongoDB.client = motor.motor_asyncio.AsyncIOMotorClient(str(MONGO_DATABASE_URL))
	mongoDB.database = mongoDB.client[settings.MONGO_DB_NAME]
	print("MongoDB connected!")


async def close_mongo_connection():
	print("Closing MongoDB connection...")
	mongoDB.client.close()
	print("MongoDB closed!")

