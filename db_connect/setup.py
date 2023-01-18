from db_connect.config import postgre_sessionLocal

"""Connect to DB and create session, and begin transaction"""

def get_db():
	db = postgre_sessionLocal()
	db.begin()
	try:
		yield db
	finally:
		db.close()

get_db()
