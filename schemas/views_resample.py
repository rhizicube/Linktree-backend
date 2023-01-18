from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

"""Serialization for User data coming from requests as well as data going to responses"""

T = TypeVar('T') # Can be anything
class ViewsResampleSchema(BaseModel):
    session_id: str
    device_name: str
    view_count: int
    profiles:int
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
    device_name: str

class UpdateView(BaseModel):
    parameter: ViewsResampleSchema = Field(...)
