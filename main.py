from fastapi import FastAPI
from schemas.models import User
from typing import List
import schemas.models, uvicorn
from db_connect.config import postgre_engine
from router import click_resample, user, profile, link, subscription, setting, profileDetails, view, view_resample
from db_connect.mongodb_utils import connect_to_mongo, close_mongo_connection

schemas.models.PostgreBase.metadata.create_all(bind=postgre_engine)
# mongo
# models.MongoBase.metadata.create_all(bind=mongo_engine)

app = FastAPI()
app.include_router(user.user_router, prefix="/api/users", tags=["user"])
app.include_router(profile.profile_router, prefix="/api/profiles", tags=["profile"])
app.include_router(link.link_router, prefix="/api/links", tags=["link"])
app.include_router(subscription.subscription_router, prefix="/api/subscriptions", tags=["subscription"])
app.include_router(setting.setting_router, prefix="/api/settings", tags=["setting"])
app.include_router(view_resample.view_router, prefix="/api/viewsresample", tags=["viewresample"])
app.include_router(click_resample.click_router, prefix="/api/clicksresample", tags=["clickresample"])
app.include_router(profileDetails.profile_detail_router, prefix="/api/profile", tags=["profiledetails"])
app.include_router(view_resample.view_router, prefix="/api/view", tags=["view"])
app.include_router(click_resample.click_router, prefix="/api/click", tags=["click"])



app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

