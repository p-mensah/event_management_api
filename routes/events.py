from fastapi import Form, File, UploadFile, HTTPException,status, APIRouter, Depends # form, file and uploaded file added for form data
from db import events_collection
from bson.objectid import ObjectId
from utils import replace_mongo_id
from typing import Annotated  # Annotated added for form data
import cloudinary
import cloudinary.uploader
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependencies.authn import authenticated



#create users router
events_router = APIRouter()

# Events endpoints
@events_router.get("/events")
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


@events_router.post("/events")
def post_event(
        title: Annotated[str, Form()], # Updated, form data handling added
        description: Annotated[str, Form()], # Updated, form data handling added
        flyer: Annotated[UploadFile, File()],
        # credintials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
        user_id = Annotated[str, Depends(authenticated)]
        ):
    # ensure an event with a title and user_id combined does nor exist
    events_count = events_collection.count_documents(filter={
"$and": [
    {"title": title},
    {"owner":  ObjectId(user_id)]}) 
    if events_count > 0:
          raise HTTPException(status.HTTP_409_CONFLICT, detail=f"Event with {title} and {user_id} already exists")  # print (credintials)
     # Updated, file handling added

    #upload flyer cloundinary to get a url
    upload_result = cloudinary.uploader.upload(flyer.file)
    # print(upload_result)
    # Insert event into database
    events_collection.insert_one({
        "title": title,
        "description": description,
        "flyer": upload_result["secure_url"],
        "owner": user_id
        })
    # # Return response
    return {"message": "Event added successfully"}


@events_router.get("/events/{event_id}")
def get_event_by_id(event_id):
    # Get event from database by id
    
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    # Return response
    if event:
        event["id"] = str(event["_id"])
        del event["_id"]
        return {"data": event}
    raise HTTPException(status_code=404, detail="Event not found")


@events_router.put("/events/{event_id}")
def replace_event(event_id,
    title: Annotated[str, Form()], # Updated, form data handling added
    description: Annotated[str, Form()], 
    flyer: Annotated[UploadFile, File()]):
    # check if event_id is valid mongo id
    # upload flyer cloundinary to get a url
    upload_result = cloudinary.uploader.upload(flyer.file)
 # replace event in database
    events_collection.replace_one(
            filter={"_id":ObjectId(event_id)},
            replacement={
                "title":title.title,
                "description": description,
                "flyer": upload_result["secure_url"],
            },
        )
    # return response
    return {"message": " Event replaced successfully"}

from fastapi import status

@events_router.delete("/events/{event_id}") #  dependencies = [Depends{is_authenticated}])
def delete_event(event_id, user_id, Annotated [str, Depends{is_authenticated}]):
    # check if event_id is valid mongo id
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid Mongo ID received")
    # delete event from database
    delete_result = events_collection.delete_one(filter={"_id": ObjectId(event_id)})
    if not delete_result.deleted_count:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No event found to delete")

    #return response

    return{"Message":"Event deleted successfully"}