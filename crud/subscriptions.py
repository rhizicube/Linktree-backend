from sqlalchemy.orm import session
from schemas.models import Subscription
from schemas.subscriptions import SubscriptionSchema
from crud.users import get_user_by_username
from fastapi import HTTPException, UploadFile, File
from sqlalchemy import func
from core.settings import settings
import secrets, os, shutil


def get_all_subscriptions(db:session, skip:int=0, limit:int=100):
    """Function to get all subscriptions in DB

    Args:
        db (session): DB connection session for ORM functionalities
        skip (int, optional): To skip X number of rows from beginning. Defaults to 0.
        limit (int, optional): Limit number of rows to be queried. Defaults to 100.

    Returns:
        orm query set: returns the queried subscriptions
    """
    return db.query(Subscription).offset(skip).limit(limit).all()

def get_subscription_by_id(db:session, id:int):
    """Function to get subscription for the given pk

    Args:
        db (session): DB connection session for ORM functionalities
        id (int): subscription primary key

    Returns:
        orm query set: returns the queried subscription
    """
    return db.query(Subscription).get(id)

def create_subscription(db:session, subscription:SubscriptionSchema):
    _subscription = Subscription(subscription_name=subscription.subscription_name, subscription_type=subscription.subscription_type, subscription_description=subscription.subscription_description, subscription_reminder=subscription.subscription_reminder)
    db.add(_subscription)
    db.commit()
    db.refresh(_subscription)
    return _subscription

def delete_all_subscriptions(db:session):
    try:
        deleted_rows = db.query(Subscription).delete()
        db.commit()
        return deleted_rows
    except Exception as e:
        db.rollback()

def delete_subscription_by_id(db:session, id:int):
    _subscription = db.query(Subscription).get(id)
    if _subscription:
        db.delete(_subscription)
        db.commit()
        return _subscription
    else:
        db.rollback()
        raise HTTPException(status_code=404, detail="Subscription not found")

def update_subscription(db:session, id:int, subscription_description:str=None, subscription_reminder:bool=None, subscription_type:str=None, subscription_name:str=None):
    _subscription = get_subscription_by_id(db, id)
    is_updated = False

    if subscription_description is not None:
        _subscription.subscription_description = subscription_description
        is_updated = True
    if subscription_reminder is not None:
        _subscription.subscription_reminder = subscription_reminder
        is_updated = True
    if subscription_type is not None:
        _subscription.subscription_type = subscription_type
        is_updated = True
    if subscription_name is not None:
        _subscription.subscription_name = subscription_name
        is_updated = True
    if is_updated:
        _subscription.subscription_updated = func.now()

    db.commit()
    db.refresh(_subscription)
    return _subscription
