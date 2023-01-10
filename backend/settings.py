from pydantic import BaseSettings
import os

class Settings(BaseSettings):
	# PostgreSQL connection
	POSTGRE_DB_ENGINE: str = "postgresql"
	POSTGRE_DB_USER: str = "admin@rhizicube.ai"
	POSTGRE_DB_PASS: str = "1234"
	POSTGRE_DB_HOST: str = "localhost"
	POSTGRE_DB_NAME: str = "rhizicubedb"
	POSTGRE_DB_PORT: int = 5432

	# MongoDB connection
	MONGO_DB_ENGINE: str = "mongodb+srv"
	MONGO_DB_USER: str = "admin@rhizicube.ai"
	MONGO_DB_PASS: str = "1234"
	MONGO_DB_HOST: str = "localhost"
	MONGO_DB_NAME: str = "rhizicubedb"
	MONGO_DB_PORT: int = 27017

	STATIC_URL = '/static/'
	MEDIA_URL = '/media/'
 
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
	MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

settings = Settings()


