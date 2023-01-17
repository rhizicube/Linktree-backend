from sqlalchemy.orm import session
from schemas.models import Setting
from schemas.settings import SettingSchema
from fastapi import HTTPException

def get_all_settings(db:session, skip:int=0, limit:int=100):
	"""Function to get all settings in DB

	Args:
		db (session): DB connection session for ORM functionalities
		skip (int, optional): To skip X number of rows from beginning. Defaults to 0.
		limit (int, optional): Limit number of rows to be queried. Defaults to 100.

	Returns:
		orm query set: returns the queried settings
	"""
	return db.query(Setting).offset(skip).limit(limit).all()


def get_setting_by_profile(db:session, profile:int):
	"""Function to get setting for the given user

	Args:
		db (session): DB connection session for ORM functionalities
		uname (str): username, foreign key

	Returns:
		orm query set: returns the queried setting
	"""
	return db.query(Setting).filter_by(profile_id=profile).first()


def get_setting_by_id(db:session, id:int):
	"""Function to get setting for the given pk

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): setting primary key

	Returns:
		orm query set: returns the queried setting
	"""
	return db.query(Setting).get(id)


def create_setting(db:session, setting:SettingSchema):
	"""Function to create a setting

	Args:
		db (session): DB connection session for ORM functionalities
		setting (SettingSchema): Serialized setting

	Returns:
		orm query set: returns created setting
	"""
	_setting = Setting(profile_social=setting.profile_social, profile_id=setting.profile)
	db.add(_setting)
	print("Here")
	db.commit()
	print("Here")
	db.refresh(_setting)
	return _setting


def delete_all_settings(db:session):
	"""Function to delete all settings

	Args:
		db (session): DB connection session for ORM functionalities

	Returns:
		int: number of rows deleted
	"""
	try:
		deleted_rows = db.query(Setting).delete()
		db.commit()
		return deleted_rows
	except Exception as e:
		db.rollback()


def delete_setting_by_id(db:session, id:int):
	"""Function to delete setting by id

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): setting primary key

	Raises:
		HTTPException: If setting for given id not found

	Returns:
		orm query set: returns deleted setting
	"""
	_setting = db.query(Setting).get(id)
	if _setting:
		db.delete(_setting)
		db.commit()
		return _setting
	else:
		db.rollback()
		raise HTTPException(status_code=404, detail="Setting not found")


def update_setting(db:session, id:int, profile_social=None):
	"""Function to update setting

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): setting primary key
		profile_social (dict, optional): Social icons. Defaults to None.

	Returns:
		orm query set: returns updated setting
	"""
	_setting = db.query(Setting).get(id)
	if profile_social is not None:
		_setting.profile_social = profile_social
	db.commit()
	db.refresh(_setting)
	return _setting
