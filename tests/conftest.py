from typing import Any
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
#this is to include backend dir in sys.path so that we can import from db,main.py

from db_connect.config import PostgreBase as Base
from db_connect.setup import get_db
from router.profile import profile_router 
from router.link import link_router
from router.setting import setting_router
from router.subscription import subscription_router
from router.view_resample import view_router
from router.click_resample import click_router
from router.profileDetails import profile_detail_router
from router.user_profile import router


def start_application():
	app = FastAPI()
	app.include_router(profile_router)
	app.include_router(link_router)
	app.include_router(setting_router)
	app.include_router(subscription_router)
	app.include_router(view_router)
	app.include_router(click_router)
	app.include_router(profile_detail_router)
	app.include_router(router)
	return app


SQLALCHEMY_DATABASE_URL = "sqlite:///./linktree_test_db.db"
engine = create_engine(
	SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# Use connect_args parameter only with sqlite
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def app() -> Generator[FastAPI, Any, None]:
	"""
	Create a fresh database on each test case.
	"""
	Base.metadata.create_all(engine)  # Create the tables.
	_app = start_application()
	yield _app
	Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
	connection = engine.connect()
	transaction = connection.begin()
	session = SessionTesting(bind=connection)
	yield session  # use the session in tests.
	session.close()
	transaction.rollback()
	connection.close()


@pytest.fixture(scope="function")
def client(
	app: FastAPI, db_session: SessionTesting
) -> Generator[TestClient, Any, None]:
	"""
	Create a new FastAPI TestClient that uses the `db_session` fixture to override
	the `get_db` dependency that is injected into routes.
	"""

	def _get_test_db():
		try:
			yield db_session
		finally:
			pass

	app.dependency_overrides[get_db] = _get_test_db
	with TestClient(app) as client:
		yield client