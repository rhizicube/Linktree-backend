from fastapi import FastAPI
import schemas.models as models
import uvicorn
from db_connect.config import postgre_engine
from router import user, profile, link, trials

from celery_config.celery_utils import create_celery


models.PostgreBase.metadata.create_all(bind=postgre_engine)

# Original
# app = FastAPI()
# app.include_router(user.user_router, prefix="/api/users", tags=["user"])
# app.include_router(profile.profile_router, prefix="/api/profiles", tags=["profile"])
# app.include_router(link.link_router, prefix="/api/links", tags=["link"])


# if __name__ == "__main__":
# 	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# Including celery setup
def create_app() -> FastAPI:
	current_app = FastAPI(title="LinkTree",
						  description="LinkTree sample application in FastAPI including API functionalities and event-driven scheduled tasks with Celery and RabbitMQ",
						  version="1.0.0", )

	current_app.celery_app = create_celery()
	current_app.include_router(user.user_router, prefix="/api/users", tags=["user"])
	current_app.include_router(profile.profile_router, prefix="/api/profiles", tags=["profile"])
	current_app.include_router(link.link_router, prefix="/api/links", tags=["link"])
	current_app.include_router(trials.router)
	return current_app


app = create_app()
celery = app.celery_app


if __name__ == "__main__":
	uvicorn.run("main:app", port=8000, reload=True)