from typing import Optional, Generic, TypeVar, Text, List
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


"""Serialization for Profile data coming from requests as well as data going to responses"""
T = TypeVar('T') 
class SettingSchema(BaseModel):
    profile_social: dict
    # profile_subscribe: bool
    profile_management:int
    class Config:
        orm_mode=True

class RequestSetting(BaseModel):
    parameter: SettingSchema = Field(...)

class ResponseSetting(GenericModel, Generic[T]):
    code: str
    status: str
    message: Optional[str]=None
    result: Optional[T]=None

class SettingUpdateSchema(BaseModel):
    profile_social: Optional[dict]=None

class UpdateSetting(BaseModel):
    parameter: SettingUpdateSchema = Field(...)