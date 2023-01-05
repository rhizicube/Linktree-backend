from typing import Optional, Generic, TypeVar, Text
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

"""Serialization for Profile data coming from requests as well as data going to responses"""

T = TypeVar('T') # Can be anything

class ProfileSchema(BaseModel):
	profile_link: str
	profile_bio: Optional[Text]=None
	username: str
	profile_image_path:Optional[str]=None

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
	profile_bio: Optional[str]=None

class UpdateProfile(BaseModel):
	parameter: ProfileUpdateSchema = Field(...)