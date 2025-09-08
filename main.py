from fastapi import FastAPI, Form, File, UploadFile, HTTPException # form, file and uploaded file added for form data
from db import events_collection
from pydantic import BaseModel
from bson.objectid import ObjectId

from utils import replace_mongo_id
from typing import Annotated  # Annotated added for form data





class EventModel(BaseModel):
    title: str
    description: str


app = FastAPI()


@app.get("/")
def get_home():
    return {"message": "You are on the home page"}


# Events endpoints
@app.get("/events")
def get_events(title="", description ="", limit = 10, skip = 0):  # Updated, title and description added
    """Retrieve all events from the database."""
    # Get all events from database
    
    events = events_collection.find(
        filter={
            "$or": [
                {"title": {"$regex": title, "$options": "i"}}, # title filter added
                {"description": {"$regex": description, "$options": "i"}} # description filter added
            ]
        },
        limit = int(limit),
        skip = int(skip)
    ).to_list()  # Updated, filter for title and descriptions added to find()
    # retrun data
    return {"data": list(map(replace_mongo_id, events))}


@app.post("/events")
def post_event(
        title: Annotated[str, Form()], # Updated, form data handling added
        description: Annotated[str, Form()], # Updated, form data handling added
        flyer: Annotated[UploadFile, File()]): # Updated, file handling added
    # Insert event into database
    # events_collection.insert_one(event.model_dump())
    # # Return response
    return {"message": "Event added successfully"}


@app.get("/events/{event_id}")
def get_event_by_id(event_id):
    # Get event from database by id
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    # Return response
    if event:
        event["id"] = str(event["_id"])
        del event["_id"]
        return {"data": event}
    raise HTTPException(status_code=404, detail="Event not found")
