from sqlalchemy.orm import session
from models import ClicksResample
from schemas.clicks import ClicksResampleSchema as ClickSchema
from fastapi import HTTPException, UploadFile, File
from sqlalchemy import func
from core.settings import settings
import secrets, os, shutil

def get_all_clicks(db:session, skip:int=0, limit:int=100):
    """Function to get all clicks in DB

    Args:
        db (session): DB connection session for ORM functionalities
        skip (int, optional): To skip X number of rows from beginning. Defaults to 0.
        limit (int, optional): Limit number of rows to be queried. Defaults to 100.

    Returns:
        orm query set: returns the queried clicks
    """
    return db.query(ClicksResample).offset(skip).limit(limit).all()

def get_click_by_id(db:session, id:int):
    """Function to get click for the given pk

    Args:
        db (session): DB connection session for ORM functionalities
        id (int): click primary key

    Returns:
        orm query set: returns the queried click
    """
    return db.query(ClicksResample).get(id)

def get_click_by_link_id(db:session, link_id:int):
    """Function to get click for the given pk

    Args:
        db (session): DB connection session for ORM functionalities
        id (int): click primary key

    Returns:
        orm query set: returns the queried click
    """
    return db.query(ClicksResample).filter_by(link_id=link_id).all()

def get_click_by_view_id(db:session, view_id:int):
    """Function to get click for the given pk

    Args:
        db (session): DB connection session for ORM functionalities
        id (int): click primary key

    Returns:
        orm query set: returns the queried click
    """
    return db.query(ClicksResample).filter_by(view_id=view_id).all()

def create_click(db:session, click:ClickSchema):
    """Function to create a click

    Args:
        db (session): DB connection session for ORM functionalities
        click (ClickSchema): Serialized click

    Returns:
        orm query set: returns created click
    """
    _click = ClicksResample(click_count=click.click_count, view_id=click.view_id, link_id=click.link_id)
    print(_click)
    db.add(_click)
    db.commit()
    db.refresh(_click)
    return _click
    

def delete_all_clicks(db:session):
    """Function to delete all clicks in DB

    Args:
        db (session): DB connection session for ORM functionalities
    """
    try:
        deleted_rows = db.query(ClicksResample).delete()
        db.commit()
        return deleted_rows
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_click_by_id(db:session, id:int):
    """Function to delete a click for the given pk

    Args:
        db (session): DB connection session for ORM functionalities
        id (int): click primary key
    """
    try:
        deleted_rows = db.query(ClicksResample).filter_by(id=id).delete()
        db.commit()
        return deleted_rows
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def update_click(db:session, click_count:int):
    """Function to update a click for the given pk

    Args:
        db (session): DB connection session for ORM functionalities
        id (int): click primary key
        click (ClickSchema): Serialized click
    """
    _click = db.query(ClicksResample).get(click_count)
    is_updated = False
    if click_count is not None:
        _click.click_count = click_count
        is_updated = True
    if is_updated:
        _click.click_updated = func.now()
    db.commit()
    db.refresh(_click)
    return _click
    
