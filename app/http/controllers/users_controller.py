from fastapi import Depends, APIRouter, HTTPException, Response, status
from dependency_injector.wiring import inject, Provide
import app.kernel as kernel
from app.http.services.users import UserService
from logging import Logger, log

route = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not found"}} 
)

@route.get("/")
@inject
async def get_users(user_service: UserService = Depends(Provide[kernel.Container.user_service])):
    result = []
    try: 
        for user in user_service.get_all(0, 100):
            print(user.deparment)
            result.append(user)
    except Exception as e:
        print(e)
    return result 

@route.get("/{id}")
@inject
async def get_user_id(id: int, user_service: UserService = Depends(Provide[kernel.Container.user_service])):
    return user_service.create_user()