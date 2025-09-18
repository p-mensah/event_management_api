
import os
import email
from fastapi import APIRouter, Form, status, HTTPException
from typing import Annotated
from db import users_collection 
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta





#create users router
users_router = APIRouter()

# Users endpoints
@users_router.post("/users/register")
def register_user(
    user_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    passwords: Annotated[str, Form(min_length=8)],
):
    #ensure user doesnt exist
    user_count = users_collection.count_documents(filter={"email": email})
    if user_count > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exist")
    
    #hash password
    hashed_password = bcrypt.hashpw(passwords.encode(), bcrypt.gensalt())
    
    #save user to database
    users_collection.insert_one({
        "user_name": user_name,
        "email": email,
        "password": hashed_password.decode('utf-8')}) # Store as string

    # return your response
    return {"message": "User registered successfully"}


@users_router.post("/users/login")
def login_user(
     email: Annotated[str, Form()],
    passwords: Annotated[str, Form(min_length=8)],

):
    # Ensure user exist
    user = users_collection.find_one(filter={"email": email})
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User does not exist")
    
    # compare the password
    correct_password = bcrypt.checkpw(passwords.encode(), user["password"].encode())
    if not correct_password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect password")
    
    # generate for them an access token
    encoded_jwt = jwt.encode(payload={"id": str(user["_id"]), "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=60)}, key=os.getenv("JWT_SECRET_KEY"), algorithm="HS256")
    
    # return response
    return { "message": "User logged in successfully","access_token": encoded_jwt}
    
