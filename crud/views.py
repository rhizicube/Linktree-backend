from schemas.models import UpdateViews
from fastapi.encoders import jsonable_encoder
from datetime import datetime as dt
from db_connect.config import mongoDB
from pymongo import ASCENDING


async def create_view_raw(cookie:str, device:str, location:dict, profile_id:str):
	"""Function to create view record in MongoDB

	Args:
		cookie (str): Session ID
		device (str): Device type
		location (dict): Location details
		profile_id (str): Profile's Custom link

	Returns:
		dict: created view record
	"""
	try:
		mongoDBConnection = mongoDB.database
		view = UpdateViews(profile_link=profile_id, session_id=cookie, device=device, location=location, view_created=dt.utcnow())
		view = jsonable_encoder(view)
		_view = await mongoDBConnection["views"].insert_one(view)
		created_view = await mongoDBConnection["views"].find_one({"_id": _view.inserted_id})
		print("Created view +++", created_view)
		return created_view
	except Exception as e:
		print('View ERROR >>>', e)


async def get_view_by_id(id):
	"""Function to get view by id

	Args:
		id (ObjectId): View id, pk

	Returns:
		dict: queried view record
	"""
	mongoDBConnection = mongoDB.database
	_view = await mongoDBConnection["views"].find_one({"_id": id})
	return _view


async def get_views_by_profile(profile):
	"""Function to get view by profile

	Args:
		id (int): Profile id

	Returns:
		dict: queried view record
	"""
	mongoDBConnection = mongoDB.database
	cursor = mongoDBConnection["views"].find().where(f"this.profile_link == {profile}").sort("session_id")
	all = await cursor.to_list(length=10000)
	return all


async def get_views_by_profile_datetime_range(profile, start=None, end=dt.strftime(dt.utcnow(), "%Y-%m-%dT%H:%M:%S")):
	"""Function to get all views for a profile between a date-time range

	Args:
		profile (int): Profile id, fk
		start (str, optional): Start time. Defaults to None.
		end (str, optional): End time. Defaults to dt.strftime(dt.utcnow(), "%Y-%m-%dT%H:%M:%S").

	Returns:
		_type_: _description_
	"""
	mongoDBConnection = mongoDB.database
	if start:
		cursor = mongoDBConnection["views"].find().where(f"this.profile_link == '{profile}' && this.view_created > '{start}' && this.view_created <= '{end}'").sort("view_created", ASCENDING)
	else:
		cursor = mongoDBConnection["views"].find().where(f"this.profile_link == '{profile}' && this.view_created <= '{end}'").sort("view_created", ASCENDING)
	all = await cursor.to_list(length=10000)
	return all


async def get_all_views():
	"""Function to get all views

	Returns:
		dict: queried view records
	"""
	mongoDBConnection = mongoDB.database
	cursor = mongoDBConnection["views"].find()
	all = await cursor.to_list(length=100)
	return all


async def delete_view_by_id(id):
	"""Function to delete view by id

	Args:
		id (ObjectId): View id, pk

	Returns:
		dict: deleted view record
	"""
	mongoDBConnection = mongoDB.database
	_view = await mongoDBConnection["views"].delete_one({"_id": id})
	return _view


async def delete_all_views():
	"""Function to delete all views

	Returns:
		dict: deleted view records
	"""
	mongoDBConnection = mongoDB.database
	_view = await mongoDBConnection["views"].delete_many({})
	return _view
