from schemas.models import UpdateClicks
from fastapi.encoders import jsonable_encoder
from datetime import datetime as dt
from db_connect.config import mongoDB


async def create_click_raw(cookie, link):
	"""Function to create click record in MongoDB

	Args:
		cookie (str): Session ID
		link (str): Link clicked on

	Returns:
		dict: created click record
	"""
	try:
		mongoDBConnection = mongoDB.database
		click = UpdateClicks(link=link, session_id=cookie, click_created=dt.utcnow())
		click = jsonable_encoder(click)
		print("Here2", click)
		_click = await mongoDBConnection["clicks"].insert_one(click)
		print("Here1", _click)
		created_click = await mongoDBConnection["clicks"].find_one({"_id": _click.inserted_id})
		print("Created click +++", created_click)
		return created_click
	except Exception as e:
		print('Click ERROR >>', e)


async def get_click_by_id(id):
	"""Function to get click by id

	Args:
		id (ObjectId): Click id, pk

	Returns:
		dict: queried click record
	"""
	mongoDBConnection = mongoDB.database
	_click = await mongoDBConnection["clicks"].find_one({"_id": id})
	return _click


async def get_all_clicks():
	"""Function to get all clicks

	Returns:
		dict: queried click records
	"""
	mongoDBConnection = mongoDB.database
	cursor = mongoDBConnection["clicks"].find()
	all = await cursor.to_list(length=100)
	return all


async def delete_click_by_id(id):
	"""Function to delete click by id

	Args:
		id (ObjectId): Click id, pk

	Returns:
		dict: deleted click record
	"""
	mongoDBConnection = mongoDB.database
	_click = await mongoDBConnection["clicks"].delete_one({"_id": id})
	return _click


async def delete_all_clicks():
	"""Function to delete all clicks

	Returns:
		dict: deleted click records
	"""
	mongoDBConnection = mongoDB.database
	_click = await mongoDBConnection["clicks"].delete_many({})
	return _click
