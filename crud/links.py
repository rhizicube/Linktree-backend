from sqlalchemy.orm import session
from schemas.models import Link
from schemas.links import LinkSchema
from .profiles import get_profile_by_id
from fastapi import HTTPException, UploadFile, File
import secrets, os, string
from utilities.generic import save_uploaded_image


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

def get_link_by_profile(db:session, profile:int):
	"""Function to get link for the given user

	Args:
		db (session): DB connection session for ORM functionalities
		profile (int): profile_id, foreign key

	Returns:
		orm query set: returns the queried link
	"""
	return db.query(Link).filter_by(profile_id=profile).first()

def create_little_link(db:session) -> str:
	"""Function to shorten links

	Args:
		db (session): DB connection session for ORM functionalities

	Returns:
		str: Short url
	"""
	# type_tiny = pyshorteners.Shortener()
	# short_url = type_tiny.tinyurl.short(long_link)
 
	# Generate a random string of 10 characters
	short_url_length = 10
	all_tiny_links = db.query(Link).with_entities(Link.link_tiny).all()
	while True:
		res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(short_url_length))
		if str(res) not in all_tiny_links:
			break
	# Convert the url to string
	short_url = str(res)
	return short_url

def create_link(db:session, link:LinkSchema):
	"""Function to create a link

	Args:
		db (session): DB connection session for ORM functionalities
		link (LinkSchema): Serialized link

	Returns:
		orm query set: returns created link
	"""
	
	short_url = create_little_link(db)
	_link = Link(link_name=link.link_name, link_url=link.link_url, link_enable=link.link_enable, link_tiny=short_url, profile_id=get_profile_by_id(db, link.profile).id)
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

def update_link(db:session, id:int, link_enable:bool=None, link_name:str=None, link_url:str=None):
	"""Function to update link

	Args:
		db (session): DB connection session for ORM functionalities
		id (int): Link id, pk
		link_enable (bool, optional): Enable flag. Defaults to None.
		link_name (str, optional): Link name. Defaults to None.
		link_url (str, optional): Link url. Defaults to None.

	Returns:
		orm query set: returns updated link
	"""
	_link = get_link_by_id(db, id)
	
	if link_enable is not None:
		_link.link_enable = link_enable
	if link_name is not None:
		_link.link_name = link_name
	if link_url is not None:
		_link.link_url = link_url
		_link.link_tiny = create_little_link(db)
	
	db.commit()
	db.refresh(_link)
	return _link

def update_link_image(db:session, id:int, file:UploadFile=File(...)):
	print(type(file))
	_link = get_link_by_id(db, id)
	img_path = save_uploaded_image(file)
	if _link.link_thumbnail not in [None, ""]:
		os.remove(_link.link_thumbnail)
	_link.link_thumbnail = img_path
	
	db.commit()
	db.refresh(_link)
	return _link