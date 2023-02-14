from typing import Optional, Generic, TypeVar, Text
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

"""Serialization for Link data coming from requests as well as data going to responses"""

T = TypeVar('T') # Can be anything

class ClicksResampleSchema(BaseModel):
    click_count: int
    view_id:int
    link_id:int
    click_sampled_timestamp: str
    class Config:
        orm_mode=True

class RequestClick(BaseModel):
    parameter: ClicksResampleSchema = Field(...)

class ResponseClick(GenericModel, Generic[T]):
    code: str
    status: str
    message: Optional[str]=None
    result: Optional[T]=None

class ClicksResampleUpdateSchema(BaseModel):
    click_count: Optional[int]=None

class UpdateClick(BaseModel):
    parameter: ClicksResampleUpdateSchema = Field(...)