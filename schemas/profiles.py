from typing import Optional, Generic, TypeVar, Text
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

"""Serialization for Profile data coming from requests as well as data going to responses"""

T = TypeVar('T') # Can be anything

class ProfileSchema(BaseModel):
	profile_name: str
	profile_link: str
	profile_bio: Optional[Text]=None
	profile_description:Optional[dict]=None
	username: str
	# subscription_id: int=None

	class Config:
		orm_mode=True

class RequestProfile(BaseModel):
	parameter: ProfileSchema = Field(...)

class ResponseProfile(GenericModel, Generic[T]):
	code: str
	status: str
	message: Optional[str]=None
	result: Optional[T]=None

class ProfileUpdateSchema(BaseModel):
	profile_name: str
	profile_link: str
	profile_bio: Optional[str]=None
	profile_description: Optional[dict]=None

class UpdateProfile(BaseModel):
	parameter: ProfileUpdateSchema = Field(...)
