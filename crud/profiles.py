from sqlalchemy.orm import session
from schemas.models import Profile
from schemas.profiles import ProfileSchema
from .users import get_user_by_username
from fastapi import HTTPException, UploadFile, File
import os
from utilities.generic import save_uploaded_image


def get_all_profiles(db:session, skip:int=0, limit:int=100):
	"""Function to get all profiles in DB

	Args:
		db (session): DB connection session for ORM functionalities
		skip (int, optional): To skip X number of rows from beginning. Defaults to 0.
		limit (int, optional): Limit number of rows to be queried. Defaults to 100.

	Returns:
		orm query set: returns the queried profiles
	"""
	return db.query(Profile).offset(skip).limit(limit).all()

def get_profile_by_id(db:session, id:int):
	"""Function to get profile for the given pk

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): profile primary key

	Returns:
		orm query set: returns the queried profile
	"""
	return db.query(Profile).get(id)

def get_profile_by_user(db:session, uname:str):
	"""Function to get profile for the given user

	Args:
		db (session): DB connection session for ORM functionalities
		uname (str): username, foreign key

	Returns:
		orm query set: returns the queried profile
	"""
	return db.query(Profile).filter_by(username=uname).first()

def create_profile(db:session, profile:ProfileSchema):
	"""Function to create a profile

	Args:
		db (session): DB connection session for ORM functionalities
		profile (ProfileSchema): Serialized profile

	Returns:
		orm query set: returns created profile
	"""
	_profile = Profile(profile_link=profile.profile_link, profile_bio=profile.profile_bio, username=get_user_by_username(db, profile.username).username)
	db.add(_profile)
	db.commit()
	db.refresh(_profile)
	return _profile

def delete_all_profiles(db:session):
	"""Function to delete profiles

	Args:
		db (session): DB connection session for ORM functionalities

	Returns:
		orm query set: returns number of deleted rows, including any cascades
	"""
	try:
		_profiles = db.query(Profile)
		_profile_img_paths = [p.profile_image_path for p in _profiles]
		deleted_rows = _profiles.delete()
		db.commit()
		for p in _profile_img_paths:
			os.remove(p.profile_image_path)
		return deleted_rows
	except Exception as e:
		db.rollback()

def delete_profile_by_id(db:session, id:int):
	"""Function to delete profile

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): profile's pk

	Raises:
		HTTPException: returns if given profile's pk is not present in DB

	Returns:
		orm query set: returns deleted profile
	"""
	_profile = db.query(Profile).get(id)
	if _profile:
		db.delete(_profile)
		db.commit()
		os.remove(_profile.profile_image_path)
		return _profile
	else:
		db.rollback()
		raise HTTPException(status_code=400, detail="Profile not found")

def update_profile(db:session, id:int, bio:str=None):
	"""Function to update profile

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): profile's pk
		bio (str, optional): Profile's bio. Defaults to None.

	Returns:
		orm query set: returns updated profile
	"""
	_profile = get_profile_by_id(db, id)
	
	if bio is not None:
		_profile.profile_bio = bio
	
	db.commit()
	db.refresh(_profile)
	return _profile

def update_profile_image(db:session, id:int, file:UploadFile=File(...)):
	"""Function to update profile image on DB

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): profile id
		file (UploadFile, optional): Uploaded image. Defaults to File(...).

	Returns:
		orm query set: returns updated profile
	"""
	print(type(file))
	_profile = get_profile_by_id(db, id)
	img_path = save_uploaded_image(file)
	print('>>>>>>>>', _profile.profile_image_path)
	if _profile.profile_image_path not in [None, ""]:
		os.remove(_profile.profile_image_path)
	_profile.profile_image_path = img_path
	
	db.commit()
	db.refresh(_profile)
	return _profile
