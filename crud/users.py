from sqlalchemy.orm import session
from schemas.models import User
from schemas.users import UserSchema
from fastapi import HTTPException
from sqlalchemy import func


def get_all_users(db:session, skip:int=0, limit:int=100):
	"""Function to get all users in DB

	Args:
		db (session): DB connection session for ORM functionalities
		skip (int, optional): To skip X number of rows from beginning. Defaults to 0.
		limit (int, optional): Limit number of rows to be queried. Defaults to 100.

	Returns:
		orm query set: returns the queried users
	"""
	return db.query(User).offset(skip).limit(limit).all()

def get_user_by_username(db:session, uname:str):
	"""Function to get user with pk

	Args:
		db (session): DB connection session for ORM functionalities
		uname (str): Username, pk

	Returns:
		orm query set: returns the queried user
	"""
	return db.query(User).get(uname)

def create_user(db:session, user:UserSchema):
	"""Function to create user

	Args:
		db (session): DB connection session for ORM functionalities
		user (UserSchema): Serialized user

	Returns:
		orm query set: returns the created user
	"""
	_user = User(username=user.username, first_name=user.first_name, last_name=user.last_name, email_id=user.email_id)
	db.add(_user)
	db.commit()
	db.refresh(_user)
	return _user

def delete_all_users(db:session):
	"""Function to delete users

	Args:
		db (session): DB connection session for ORM functionalities

	Returns:
		orm query set: returns number of deleted rows, including any cascades
	"""
	try:
		deleted_rows = db.query(User).delete()
		db.commit()
		return deleted_rows
	except Exception as e:
		db.rollback()

def delete_user(db:session, uname:str):
	"""Function to delete user

	Args:
		db (session): DB connection session for ORM functionalities
		uname (str): username, pk

	Raises:
		HTTPException: if User not found

	Returns:
		orm query set: returns the deleted user
	"""
	_user = get_user_by_username(db, uname)
	if _user:
		db.delete(_user)
		db.commit()
		return _user
	else:
		raise HTTPException(status_code=400, detail="User not found")

def update_user(db:session, uname:str=None, first_name:str=None, last_name:str=None, email_id:str=None):
	"""_summary_

	Args:
		db (session): DB connection session for ORM functionalities
		uname (str, optional): username, pk. Defaults to None.
		first_name (str, optional): User's first name. Defaults to None.
		last_name (str, optional): User's last name. Defaults to None.
		email_id (str, optional): User's email id. Defaults to None.

	Returns:
		orm query set: returns the updated user
	"""
	_user = get_user_by_username(db, uname)
	is_updated = False
	
	if first_name is not None: # != "":
		_user.first_name = first_name
		is_updated = True
	if last_name is not None: # != "":
		_user.last_name = last_name    
		is_updated = True
	if email_id is not None: # != "":
		_user.email_id = email_id
		is_updated = True
	
	if is_updated:
		# _user.user_updated = dt.now()
		_user.user_updated = func.now()
	
	db.commit()
	db.refresh(_user)
	return _user