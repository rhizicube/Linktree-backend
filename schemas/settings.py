from typing import Optional, Generic, TypeVar, Text
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
import json

"""Serialization for Setting data coming from requests as well as data going to responses"""

T = TypeVar('T') # Can be anything

class SettingSchema(BaseModel):
	profile_social: dict
	profile: int

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