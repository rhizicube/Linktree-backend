from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from config import PostgreBase
from datetime import datetime as dt
from sqlalchemy.orm import relationship
import json
from sqlalchemy.dialects.postgresql import JSON
# from sqlalchemy_imageattach.entity import Image, image_attachment


class User(PostgreBase):
	__tablename__ = "user"

	username=Column(String, primary_key=True)
	first_name=Column(String, index=True, nullable=True)
	last_name=Column(String, index=True, nullable=True)
	email_id=Column(String, index=True, nullable=False)
	user_created=Column(DateTime, server_default=func.now())
	
	profiles = relationship("Profile", back_populates="user")


class Profile(PostgreBase):
	__tablename__ = "profile"
	
	id=Column(Integer, primary_key=True, autoincrement=True)
	profile_link=Column(String, nullable=False, unique=True)
	profile_bio=Column(Text, nullable=True)
	profile_image_path=Column(String, nullable=True)
	profile_created=Column(DateTime, server_default=func.now())
	username = Column(String, ForeignKey("user.username"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")

	user = relationship("User", back_populates="profiles")
	links = relationship("Link", back_populates="profile")
	settings = relationship("Setting", back_populates="profile")
	views = relationship("View", back_populates="profile")




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
	clicks = relationship("Click", back_populates="link")



class Subscription(PostgreBase):
	__tablename__ = "subscription"

	id=Column(Integer, primary_key=True, autoincrement=True)
	subscription_name=Column(String, nullable=False, unique=True)
	subscription_type=Column(String, nullable=False)
	valid_from = Column(DateTime, nullable=True)
	valid_to = Column(DateTime, nullable=True)
	subscription_description=Column(Text, nullable=True)
	subscription_reminder = Column(Boolean, nullable=False)

class Setting(PostgreBase):
	__tablename__ = "setting"

	id=Column(Integer, primary_key=True, autoincrement=True)
	# payment_option=Column(String, nullable=False)
	# profile_subscribe=Column(Boolean, nullable=False)
	profile_social = Column(JSON, nullable=True)
	profile_management = Column(Integer, ForeignKey("profile.id"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")
	profile = relationship("Profile", back_populates="settings")

class View(PostgreBase):
	__tablename__ = "view"

	id=Column(Integer, primary_key=True, autoincrement=True)
	session_id=Column(String, nullable=False)
	device_name=Column(String, nullable=False)
	view_count = Column(Integer, nullable=False)
	view_location = Column(String, nullable=True)
	session_created = Column(DateTime, server_default=func.now())
	profile_management=Column(Integer, ForeignKey("profile.id"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")
	profile = relationship("Profile", back_populates="views")
	clicks = relationship("Click", back_populates="view")


class Click(PostgreBase):
	__tablename__ = "click"

	id=Column(Integer, primary_key=True, autoincrement=True)
	click_count=Column(Integer, nullable=False)
	click_created=Column(DateTime, server_default=func.now())
	view_id=Column(Integer, ForeignKey("view.id"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")
	link_id=Column(Integer, ForeignKey("link.id"), nullable=False, server_onupdate="CASCADE", server_ondelete="CASCADE")
	link = relationship("Link", back_populates="clicks")
	view = relationship("View", back_populates="clicks")