from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from core.settings import settings

from pymongo import MongoClient



"""To configure connection to DB"""

POSTGRE_DATABASE_URL = f"{settings.POSTGRE_DB_ENGINE}://{settings.POSTGRE_DB_USER}:{settings.POSTGRE_DB_PASS}@{settings.POSTGRE_DB_HOST}:{settings.POSTGRE_DB_PORT}/{settings.POSTGRE_DB_NAME}"

# pool_size is the largest number of connections that will be kept persistently in the pool
postgre_engine = create_engine(POSTGRE_DATABASE_URL, poolclass=QueuePool, pool_pre_ping=True, pool_size=10, max_overflow=0, connect_args={"options": "-c timezone=utc"})

# To debug with sqlalchemy logs
# postgre_engine = create_engine(POSTGRE_DATABASE_URL, echo="debug", poolclass=QueuePool, pool_pre_ping=True, pool_size=10, max_overflow=0, connect_args={"options": "-c timezone=utc"})

postgre_sessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=postgre_engine)
PostgreBase = declarative_base()


MONGO_DATABASE_URL=f"{settings.MONGO_DB_ENGINE}://{settings.MONGO_DB_USER}:{settings.MONGO_DB_PASS}@{settings.MONGO_DB_HOST}/{settings.MONGO_DB_NAME}?retryWrites=true&w=majority"
mongo_client = MongoClient(settings.MONGO_DB_HOST, settings.MONGO_DB_PORT)

