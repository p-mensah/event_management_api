
from fastapi import FastAPI # form, file and uploaded file added for form data
from routes.events import events_router
from routes.users import users_router
from dotenv import load_dotenv
import os

import cloudinary

load_dotenv()

# cloudinary.config{
# cloud_name  = os.getenv("CLOUD_NAME"),
# api_key     = get.env("API_KEY"),
# api_secret  = 
# }

app = FastAPI()

@app.get("/")
def get_home():
    return {"message": "You are on the home page"}

#include routers
app.include_router(users_router)
app.include_router(events_router)
