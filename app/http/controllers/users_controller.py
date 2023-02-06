from fastapi import Depends, APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container
from app.http.services import UserService, ResponseList, UserRequestCreateUser

route = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not found"}} 
)

@route.get("/", status_code = 200)
@inject
async def get_users(
    response: Response,
    page: int = 1,
    size: int = 100,
    user_service: UserService = Depends(Provide[Container.user_service])
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
        print("error --------------------")
        print(e)
        print("error --------------------")
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
    user_service: UserService = Depends(Provide[Container.user_service])
    ):
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

@route.post("/")
@inject
async def add_user(item: UserRequestCreateUser, user_service: UserService = Depends(Provide[Container.user_service])):
    return user_service.create_user(item)