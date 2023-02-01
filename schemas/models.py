from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from db_connect.config import PostgreBase
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime as dt
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON



""" All PostgreSQL models """

class Profile(PostgreBase):
	__tablename__ = "profile"
	
	id=Column(Integer, primary_key=True, autoincrement=True)
	profile_name=Column(String, nullable=True, unique=True)
	profile_link=Column(String, nullable=False, unique=True)
	profile_bio=Column(Text, nullable=True)
	profile_image_path=Column(String, nullable=True)
	profile_description=Column(Text, nullable=True)
	profile_created=Column(DateTime, server_default=func.now())
	username = Column(String, nullable=False, unique=True)
	subscription_id = Column(Integer, ForeignKey("subscription.id"), nullable=True, server_onupdate="SET NULL", server_ondelete="SET NULL")

	subscription = relationship("Subscription", back_populates="profile")
	links = relationship("Link", cascade="all,delete", backref="parent")
	settings = relationship("Setting", cascade="all,delete", backref="parent")
	views = relationship("ViewsResample", cascade="all,delete", backref="parent")


class Link(PostgreBase):
	__tablename__ = "link"

	id=Column(Integer, primary_key=True, autoincrement=True)
	link_name=Column(String, nullable=False)
	link_url=Column(String, nullable=False, unique=True)
	link_tiny=Column(String, nullable=False, unique=True)
	link_thumbnail=Column(String, nullable=True)
	link_enable=Column(Boolean, nullable=False)
	link_created=Column(DateTime, server_default=func.now())
	profile_id=Column(Integer, ForeignKey("profile.id"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")

	profile=relationship("Profile", back_populates="links")
	clicks=relationship("ClicksResample", back_populates="link")


class Setting(PostgreBase):
	__tablename__ = "setting"

	id=Column(Integer, primary_key=True, autoincrement=True)
	# payment_option=Column(String, nullable=False)
	# profile_subscribe=Column(Boolean, nullable=False)
	profile_social = Column(JSON, nullable=True)
	profile_id = Column(Integer, ForeignKey("profile.id"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")
	profile = relationship("Profile", back_populates="settings")


class Subscription(PostgreBase):
	__tablename__ = "subscription"

	id=Column(Integer, primary_key=True, autoincrement=True)
	subscription_name=Column(String, nullable=False, unique=True)
	subscription_type=Column(String, nullable=False)
	valid_from = Column(DateTime, nullable=True)
	valid_to = Column(DateTime, nullable=True)
	subscription_description=Column(Text, nullable=True)
	subscription_reminder = Column(Boolean, nullable=False)
 
	profile = relationship("Profile", back_populates="subscription")


class ViewsResample(PostgreBase):
	__tablename__ = "viewsresample"

	id=Column(Integer, primary_key=True, autoincrement=True)
	session_id=Column(String, nullable=False)
	device_type=Column(String, nullable=False)
	view_count=Column(Integer, nullable=False)
	view_location=Column(JSON, nullable=True)
	view_sampled_timestamp=Column(DateTime, nullable=False)
	view_created=Column(DateTime, server_default=func.now())
	profile_id=Column(Integer, ForeignKey("profile.id"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")
 
	profile=relationship("Profile", back_populates="views")
	clicks=relationship("ClicksResample", back_populates="view")


class ClicksResample(PostgreBase):
	__tablename__ = "clicksresample"

	id=Column(Integer, primary_key=True, autoincrement=True)
	click_count=Column(Integer, nullable=False)
	click_created=Column(DateTime, server_default=func.now())
	click_sampled_timestamp=Column(DateTime, nullable=False)
	view_id=Column(Integer, ForeignKey("viewsresample.id"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")
	link_id=Column(Integer, ForeignKey("link.id"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")
 
	link=relationship("Link", back_populates="clicks")
	view=relationship("ViewsResample", back_populates="clicks")



""" All MongoDB models """

class PyObjectId(ObjectId):
	@classmethod
	def __get_validators__(cls):
		yield cls.validate

	@classmethod
	def validate(cls, v):
		if not ObjectId.is_valid(v):
			raise ValueError("Invalid objectid")
		return ObjectId(v)

	@classmethod
	def __modify_schema__(cls, field_schema):
		field_schema.update(type="string")


class Views(BaseModel):
	id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
	profile_link: str = Field(...)
	session_id: str = Field(...)
	device: str = Field(...)
	location: dict = Field(...)
	view_created: dt = dt.utcnow()
	
	class Config:
		allow_population_by_field_name = True
		arbitrary_types_allowed = True
		json_encoders = {ObjectId: str}


class UpdateViews(BaseModel):
	profile_link: Optional[str]
	session_id: Optional[str]
	device: Optional[str]
	location: Optional[dict]
	view_created: dt = dt.utcnow()

	class Config:
		arbitrary_types_allowed = True
		json_encoders = {ObjectId: str}


class Clicks(BaseModel):
	id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
	link: str = Field(...)
	session_id: str = Field(...)
	click_created: dt = dt.utcnow()
	
	class Config:
		allow_population_by_field_name = True
		arbitrary_types_allowed = True
		json_encoders = {ObjectId: str}


class UpdateClicks(BaseModel):
	link: Optional[str]
	session_id: Optional[str]
	click_created: dt = dt.utcnow()

	class Config:
		arbitrary_types_allowed = True
		json_encoders = {ObjectId: str}
