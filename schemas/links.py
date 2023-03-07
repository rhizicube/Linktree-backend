from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

"""Serialization for Link data coming from requests as well as data going to responses"""

T = TypeVar('T') # Can be anything

class LinkSchema(BaseModel):
	link_name: str
	link_url: str
	link_enable:Optional[bool]=True
	link_thumbnail:Optional[str]=None
	profile: Optional[int]=None
	setting: Optional[int]=None

	class Config:
		orm_mode=True

class RequestLink(BaseModel):
	parameter: LinkSchema = Field(...)

class ResponseLink(GenericModel, Generic[T]):
	code: str
	status: str
	message: Optional[str]=None
	result: Optional[T]=None

class LinkUpdateSchema(BaseModel):
	link_name: Optional[str]=None
	link_url: Optional[str]=None
	link_thumbnail:Optional[str]=None
	link_enable: Optional[bool]=None

class UpdateLink(BaseModel):
	parameter: LinkUpdateSchema = Field(...)
