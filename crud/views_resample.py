from sqlalchemy.orm import session
from schemas.models import ViewsResample
from schemas.views_resample import ViewsResampleSchema as ViewSchema
from fastapi import HTTPException
from datetime import datetime as dt
from sqlalchemy import func

def get_all_views(db:session, skip:int=0, limit:int=100):
    """Function to get all views in DB

    Args:
        db (session): DB connection session for ORM functionalities
        skip (int, optional): To skip X number of rows from beginning. Defaults to 0.
        limit (int, optional): Limit number of rows to be queried. Defaults to 100.

    Returns:
        orm query set: returns the queried views
    """
    return db.query(ViewsResample).offset(skip).limit(limit).all()

def get_view_by_id(db:session, id:int):
    """Function to get view for the given pk

    Args:
        db (session): DB connection session for ORM functionalities
        id (int): view primary key

    Returns:
        orm query set: returns the queried view
    """
    return db.query(ViewsResample).get(id)

def get_views_by_profile_id(db:session, profile_id:int, skip:int=0, limit:int=100):
    """Function to get views for the given profile id

    Args:
        db (session): DB connection session for ORM functionalities
        profile_id (int): profile id
        skip (int, optional): To skip X number of rows from beginning. Defaults to 0.
        limit (int, optional): Limit number of rows to be queried. Defaults to 100.

    Returns:
        orm query set: returns the queried views
    """
    return db.query(ViewsResample).filter(ViewsResample.profile_id == profile_id).offset(skip).limit(limit).all()

def create_view(db:session, view:ViewSchema):
    """Function to create view

    Args:
        db (session): DB connection session for ORM functionalities
        view (ViewSchema): Serialized view

    Returns:
        orm query set: returns the created view
    """
    _view = ViewsResample(session_id=view.session_id,view_count=view.view_count, profile_id=view.profiles, device_type=view.device_name, view_sampled_timestamp=view.view_sampled_timestamp)
    db.add(_view)
    db.commit()
    db.refresh(_view)
    return _view

def delete_all_views(db:session):
    """Function to delete views

    Args:
        db (session): DB connection session for ORM functionalities

    Returns:
        orm query set: returns number of deleted rows, including any cascades
    """
    try:
        deleted_rows = db.query(ViewsResample).delete()
        db.commit()
        return deleted_rows
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_view(db:session, view_id:int):
    """Function to delete view

    Args:
        db (session): DB connection session for ORM functionalities
        view_id (int): view id

    Returns:
        orm query set: returns number of deleted rows, including any cascades
    """
    try:
        deleted_rows = db.query(ViewsResample).filter(ViewsResample.id==view_id).delete()
        db.commit()
        return deleted_rows
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def update_view(db:session, view_id:int, view_count:int=None, device_name:str=None):
    """Function to update view

    Args:
        db (session): DB connection session for ORM functionalities
        view_id (int): view id
        view (ViewSchema): Serialized view

    Returns:
        orm query set: returns the updated view
    """
    _view = db.query(ViewsResample).filter(ViewsResample.id==view_id).first()
    is_updated = False
    if view_count is not None:
        _view.view_count = _view.view_count
        is_updated = True
    if device_name is not None:
        _view.device_name = _view.device_name
        is_updated = True
    if is_updated:
        _view.view_updated = dt.now()

    db.commit()
    db.refresh(_view)
    return _view
