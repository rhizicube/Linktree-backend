from fastapi import FastAPI
from models import User
from typing import List
import models, uvicorn
from config import postgre_engine
from router import user, profile, link


models.PostgreBase.metadata.create_all(bind=postgre_engine)

app = FastAPI()
app.include_router(user.user_router, prefix="/api/users", tags=["user"])
app.include_router(profile.profile_router, prefix="/api/profiles", tags=["profile"])
app.include_router(link.link_router, prefix="/api/links", tags=["link"])


if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

