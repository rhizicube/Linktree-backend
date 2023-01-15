from fastapi import FastAPI
from models import User
from typing import List
import models, uvicorn
from db_connect.config import postgre_engine
from router import user, profile, link, subscription, setting, view, click, profileDetails, view_mongo, click_mongo
from db_connect.mongodb_utils import connect_to_mongo, close_mongo_connection

models.PostgreBase.metadata.create_all(bind=postgre_engine)
# mongo
# models.MongoBase.metadata.create_all(bind=mongo_engine)

app = FastAPI()
app.include_router(user.user_router, prefix="/api/users", tags=["user"])
app.include_router(profile.profile_router, prefix="/api/profiles", tags=["profile"])
app.include_router(link.link_router, prefix="/api/links", tags=["link"])
app.include_router(subscription.subscription_router, prefix="/api/subscriptions", tags=["subscription"])
app.include_router(setting.setting_router, prefix="/api/settings", tags=["setting"])
app.include_router(view.view_router, prefix="/api/views", tags=["view"])
app.include_router(click.click_router, prefix="/api/clicks", tags=["click"])
app.include_router(profileDetails.profile_detail_router, prefix="/api/profile", tags=["profiledetails"])
app.include_router(view_mongo.view_mongo_router, prefix="/api/viewmongo", tags=["viewmongo"])
app.include_router(click_mongo.click_mongo_router, prefix="/api/clickmongo", tags=["clickmongo"])



app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

