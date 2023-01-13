from fastapi import Depends, APIRouter, HTTPException, Response, status
from dependency_injector.wiring import inject, Provide
import kernel
from app.services.users import UserService

route = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not found"}}
)


@route.get("/")
async def get_users():
    return {"users": "Hello world"}

@route.get("/{id}")
@inject
async def get_user_id(id: int, user_service: UserService = Depends(Provide[kernel.Container.user_service])):
    user_service.create_user()
    return user_service.get_users(), id