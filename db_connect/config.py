from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from core.settings import settings
from pymongo import MongoClient
import urllib
# import motor.motor_asyncio





"""To configure connection to DB"""

POSTGRE_DATABASE_URL = f"{settings.POSTGRE_DB_ENGINE}://{settings.POSTGRE_DB_USER}:{settings.POSTGRE_DB_PASS}@{settings.POSTGRE_DB_HOST}:{settings.POSTGRE_DB_PORT}/{settings.POSTGRE_DB_NAME}"

postgre_engine = create_engine(POSTGRE_DATABASE_URL, connect_args={"options": "-c timezone=utc"})
postgre_sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgre_engine)
PostgreBase = declarative_base()
# MongoBase = declarative_base()

engine=create_engine("postgresql://{YOUR_DATABASE_USER}:{YOUR_DATABASE_PASSWORD}@localhost/{YOUR_DATABASE_NAME}",
    echo=True
)
# mongo_engine = create_engine(POSTGRE_DATABASE_URL, connect_args={"options": "-c timezone=utc"})


MONGO_DATABASE_URL=f"{settings.MONGO_DB_ENGINE}://{urllib.parse.quote_plus(settings.MONGO_DB_USER)}:{urllib.parse.quote_plus(settings.MONGO_DB_PASS)}@{settings.MONGO_DB_HOST}/{settings.MONGO_DB_NAME}?retryWrites=true&w=majority"
mongo_client = MongoClient(settings.MONGO_DB_HOST, settings.MONGO_DB_PORT)
db = mongo_client["rhizicubedb"]

# connect to mongo using pymongo

