from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

"""Serialization for User data coming from requests as well as data going to responses"""

T = TypeVar('T') # Can be anything

class UserSchema(BaseModel):
	username: str
	first_name: Optional[str]=None
	last_name: Optional[str]=None
	email_id: str
	profiles: Optional[List]=None

	class Config:
		orm_mode=True
	
class RequestUser(BaseModel):
	parameter: UserSchema = Field(...)

class ResponseUser(GenericModel, Generic[T]):
	code: str
	status: str
	message: Optional[str]=None
	result: Optional[T]=None

class UserUpdateSchema(BaseModel):
	first_name: Optional[str]=None
	last_name: Optional[str]=None
	email_id: Optional[str]=None

class UpdateUser(BaseModel):
	parameter: UserUpdateSchema = Field(...)