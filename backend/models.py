from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Boolean
from config import PostgreBase
from datetime import datetime as dt
from sqlalchemy.orm import relationship
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
