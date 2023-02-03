from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from datetime import datetime as dt
"""Serialization for User data coming from requests as well as data going to responses"""

T = TypeVar('T') # Can be anything
class ViewsResampleSchema(BaseModel):
	session_id: str
	device_type: str
	view_count: int
	view_location: dict
	view_sampled_timestamp: dt
	profile: int
	class Config:
		orm_mode=True

class RequestView(BaseModel):
	parameter: ViewsResampleSchema = Field(...)

class ResponseView(GenericModel, Generic[T]):
	code: str
	status: str
	message: Optional[str]=None
	result: Optional[T]=None

class ViewsResampleUpdateSchema(BaseModel):
	view_count: int
	device_type: str
	view_location: dict
	view_sampled_timestamp: str

class UpdateView(BaseModel):
	parameter: ViewsResampleSchema = Field(...)
