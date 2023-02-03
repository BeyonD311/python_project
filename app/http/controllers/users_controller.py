from fastapi import Depends, APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide
import app.kernel as kernel
from app.http.services import UserService, factory_base_model, UserResponse
from pydantic import create_model

route = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not found"}} 
)

@route.get("/", status_code = 200)
@inject
async def get_users(
    page: int,
    size: int,
    response: Response,
    user_service: UserService = Depends(Provide[kernel.Container.user_service])
    ):
    result = []
    if page == 1 or page <= 0:
        page = 0
    else:
        page = page - 1
    try: 
        result = user_service.get_all(page, size)
    except Exception as e:
        response.status_code = status.HTTP_417_EXPECTATION_FAILED
        print(e)
        return {
            "status": "fail",
            "message": e
        }
    return result

@route.get("/{id}")
@inject
async def get_user_id(
    id: int, 
    response: Response,
    user_service: UserService = Depends(Provide[kernel.Container.user_service])
    ):
    result = UserResponse()
    try:
        user = user_service.get_user_by_id(id)
        user.deparment
        user.roles
        user.position
        user.group_user
        return user
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "status": "fail",
            "message": "Not found user"
        }
