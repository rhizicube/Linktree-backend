from typing import Optional, Generic, TypeVar, Text
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

"""Serialization for Link data coming from requests as well as data going to responses"""
T = TypeVar('T')

class SubscriptionSchema(BaseModel):
    subscription_name: str
    subscription_type: str
    # valid_from: Optional[datetime]=None
    # valid_to: Optional[datetime]=None
    subscription_description: Optional[Text]=None
    subscription_reminder: bool
    class Config:
        orm_mode=True

class RequestSubscription(BaseModel):
    parameter: SubscriptionSchema = Field(...)

class ResponseSubscription(GenericModel, Generic[T]):
    code: str
    status: str
    message: Optional[str]=None
    result: Optional[T]=None

class SubscriptionUpdateSchema(BaseModel):
    subscription_name: Optional[str]=None
    subscription_type: Optional[str]=None
    subscription_description: Optional[Text]=None
    subscription_reminder: Optional[bool]=None

class UpdateSubscription(BaseModel):
    parameter: SubscriptionUpdateSchema = Field(...)