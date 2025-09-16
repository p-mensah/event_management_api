
from fastapi import APIRouter, Form, status, HTTPException
from typing import Annotated
from db import users_collection

import bcrypt
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
    hashed_password = bcrypt.hashpw(passwords.encode('utf-8'), bcrypt.gensalt())
    
    #save user to database
    users_collection.insert_one({
        "user_name": user_name,
        "email": email,
        "password": hashed_password.decode('utf-8')}) # Store as string

    # return your response
    return {"message": "User registered successfully"}


# @users_router.post("/users/login")
# def login_user():
#     return {"message": "User logged in successfully"}
    
