from fastapi import Depends, APIRouter, HTTPException, Response, status
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from app.services.users import UserLoginParams

route = APIRouter()

@route.post("/login")
def login():
    return "Hello am test case"

@route.get("/logout")
def logout():
    return "logout"

@route.get("refresh")
def refresh():
    return "refresh"