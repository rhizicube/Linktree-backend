from fastapi import FastAPI
import schemas.models as models
import uvicorn
from db_connect.config import postgre_engine
from router import user, profile, link, trials, user_profile, setting, view, click
from db_connect.setup import connect_to_mongo, close_mongo_connection
from celery_config.celery_utils import create_celery

models.PostgreBase.metadata.create_all(bind=postgre_engine)


def create_app() -> FastAPI:
	current_app = FastAPI(title="LinkTree",
						  description="LinkTree sample application in FastAPI including API functionalities and event-driven scheduled tasks with Celery and RabbitMQ",
						  version="1.0.0", )

	current_app.celery_app = create_celery()
	current_app.include_router(user.user_router, prefix="/api/users", tags=["user"])
	current_app.include_router(profile.profile_router, prefix="/api/profiles", tags=["profile"])
	current_app.include_router(link.link_router, prefix="/api/links", tags=["link"])
	current_app.include_router(setting.setting_router, prefix="/api/settings", tags=["setting"])
	current_app.include_router(trials.router)
	current_app.include_router(user_profile.router, tags=["Visitor"])
	current_app.include_router(view.view_router, tags=["View"])
	current_app.include_router(click.click_router, tags=["Click"])
	return current_app


app = create_app()

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

celery = app.celery_app


if __name__ == "__main__":
	uvicorn.run("main:app", port=8000, proxy_headers=True, forwarded_allow_ips=["*"], reload=True)
