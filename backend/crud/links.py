from sqlalchemy.orm import session
from models import Link
from schemas.links import LinkSchema
from crud.profiles import get_profile_by_id
from fastapi import HTTPException, UploadFile, File
from sqlalchemy import func
from settings import settings
import secrets, os, shutil


def get_all_links(db:session, skip:int=0, limit:int=100):
	"""Function to get all links in DB

	Args:
		db (session): DB connection session for ORM functionalities
		skip (int, optional): To skip X number of rows from beginning. Defaults to 0.
		limit (int, optional): Limit number of rows to be queried. Defaults to 100.

	Returns:
		orm query set: returns the queried links
	"""
	return db.query(Link).offset(skip).limit(limit).all()

def get_link_by_id(db:session, id:int):
	"""Function to get link for the given pk

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): link primary key

	Returns:
		orm query set: returns the queried link
	"""
	return db.query(Link).get(id)

def get_link_by_profile(db:session, profile_id:int):
	"""Function to get link for the given user

	Args:
		db (session): DB connection session for ORM functionalities
		uname (str): username, foreign key

	Returns:
		orm query set: returns the queried link
	"""
	return db.query(Link).filter_by(profile_id=profile_id).all()

def create_link(db:session, link:LinkSchema):
	"""Function to create a link

	Args:
		db (session): DB connection session for ORM functionalities
		link (LinkSchema): Serialized link

	Returns:
		orm query set: returns created link
	"""
	_link = Link(link_name=link.link_name, link_thumbnail=link.link_thumbnail, link_url=link.link_url, link_enable=link.link_enable, link_tiny=link.link_tiny, profile_id=link.profile_id)
	db.add(_link)
	db.commit()
	db.refresh(_link)
	return _link

def delete_all_links(db:session):
	"""Function to delete links

	Args:
		db (session): DB connection session for ORM functionalities

	Returns:
		orm query set: returns number of deleted rows, including any cascades
	"""
	try:
		deleted_rows = db.query(Link).delete()
		db.commit()
		return deleted_rows
	except Exception as e:
		db.rollback()

def delete_link_by_id(db:session, id:int):
	"""Function to delete link

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): link's pk

	Raises:
		HTTPException: returns if given link's pk is not present in DB

	Returns:
		orm query set: returns deleted link
	"""
	_link = db.query(Link).get(id)
	if _link:
		db.delete(_link)
		db.commit()
		return _link
	else:
		db.rollback()
		raise HTTPException(status_code=400, detail="Link not found")

def update_link(db:session, id:int, bio:str=None):
	"""Function to update link

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): link's pk
		bio (str, optional): Link's bio. Defaults to None.

	Returns:
		orm query set: returns updated link
	"""
	_link = get_link_by_id(db, id)
	is_updated = False
	
	if bio is not None:
		_link.link_bio = bio
		is_updated = True
	if is_updated:
		_link.link_updated = func.now()
	
	db.commit()
	db.refresh(_link)
	return _link

def create_link_image(file:UploadFile=File(...)):
	filename, file_extension = os.path.splitext(file.filename)
	img_token = secrets.token_hex(10) + file_extension
	img_path = os.path.join(settings.STATIC_ROOT, img_token)
	with open(img_path, 'wb') as f:
		shutil.copyfileobj(file.file, f)
	return img_path

def update_link_image(db:session, id:int, file:UploadFile=File(...)):
	print(type(file))
	_link = get_link_by_id(db, id)
	img_path = create_link_image(file)
	if _link.link_image_path not in [None, ""]:
		os.remove(_link.link_image_path)
	_link.link_image_path = img_path
	_link.link_updated = func.now()
	
	db.commit()
	db.refresh(_link)
	return _link
