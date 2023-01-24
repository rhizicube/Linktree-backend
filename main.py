from fastapi import FastAPI, APIRouter
import schemas.models as models
import uvicorn
from db_connect.config import postgre_engine
from router import profile, link, trials, user_profile, setting, view, click, profileDetails
# from router import user_profile, profileDetails
from db_connect.setup import connect_to_mongo, close_mongo_connection
from celery_config.celery_utils import create_celery
from fastapi.middleware.cors import CORSMiddleware

models.PostgreBase.metadata.create_all(bind=postgre_engine)

main_router = APIRouter()

def include_routers():
	# main_router.include_router(user.user_router, prefix="/api/users", tags=["user"])
	main_router.include_router(profile.profile_router, prefix="/api/profiles", tags=["profile"])
	main_router.include_router(link.link_router, prefix="/api/links", tags=["link"])
	main_router.include_router(setting.setting_router, prefix="/api/settings", tags=["setting"])
	# main_router.include_router(trials.router)
	main_router.include_router(user_profile.router, prefix="/api", tags=["Visitor"])
	main_router.include_router(profileDetails.profile_detail_router, prefix='/api/profile', tags=["User"])
	# main_router.include_router(view.view_router, tags=["View"])
	# main_router.include_router(click.click_router, tags=["Click"])


def create_app() -> FastAPI:
	current_app = FastAPI(title="LinkTree",
						  description="LinkTree sample application in FastAPI including API functionalities and event-driven scheduled tasks with Celery and RabbitMQ",
						  version="1.0.0", )

	current_app.celery_app = create_celery()
	include_routers()
	current_app.include_router(main_router)
	return current_app


app = create_app()

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

celery = app.celery_app


if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, proxy_headers=True, forwarded_allow_ips=["*"], reload=True)
