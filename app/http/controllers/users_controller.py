import inspect
from fastapi import Depends, APIRouter, Response, status, UploadFile, Body, File
from typing import List
from datetime import datetime
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container
from app.http.services import UserService, UserRequest
from app.database import NotFoundError

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
    size: int = 10,
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
            "message": str(e)
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
async def add_user(
    response: Response,
    email: str = Body(),
    password: str = Body(),
    name: str = Body(),
    last_name: str = Body(),
    patronymic: str = Body(default=None),
    login: str = Body(),
    is_operator: bool = Body(default=False),
    deparment_id: int = Body(),
    position_id: int = Body(),
    group_id: List[str] = Body(),
    roles_id: List[str] = Body(),
    date_employment_at: datetime = Body(default=datetime.now()),
    date_dismissal_at: datetime = Body(default=None),
    phone: str = Body(default=None),
    inner_phone: int|str = Body(default=None),
    image: UploadFile|str = File(default=None),
    user_service: UserService = Depends(Provide[Container.user_service])
    ):

    if check_file(image):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "not an image uploaded"
        } 
    if bool(image) == False:
        image = None
    if bool(inner_phone) == False:
        inner_phone = None
    if len(group_id) > 0:
        group_id = group_id[0].split(",")
    if len(roles_id) > 0:
        roles_id = roles_id[0].split(",")

    user_request = UserRequest(
        email=email,
        password = password,
        login = login,
        name = name,
        last_name = last_name,
        patronymic = patronymic,
        fio=f"{name} {last_name} {patronymic}".strip(),
        is_operator = is_operator,
        deparment_id = deparment_id,
        position_id = position_id,
        group_id = group_id,
        roles_id = roles_id,
        date_employment_at = date_employment_at,
        phone = phone,
        inner_phone = inner_phone,
        date_dismissal_at = date_dismissal_at,
        image = image,
    )
    user = user_service.create_user(user_request)
    if type(user) == tuple:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "Bad request"
        }
    return user

@route.put("/{id}")
@inject
async def add_user(
    id: int,
    response: Response,
    email: str = Body(),
    password: str = Body(),
    name: str = Body(),
    last_name: str = Body(),
    patronymic: str = Body(default=None),
    login: str = Body(),
    is_operator: bool = Body(default=False),
    deparment_id: int = Body(),
    position_id: int = Body(),
    group_id: List[str] = Body(),
    roles_id: List[str] = Body(),
    date_employment_at: datetime = Body(default=datetime.now()),
    date_dismissal_at: datetime = Body(default=datetime.now()),
    phone: str = Body(default=None),
    inner_phone: int|str = Body(default=None),
    image: UploadFile|str = File(default=None),
    user_service: UserService = Depends(Provide[Container.user_service])
    ):
    if check_file(image):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "not an image uploaded"
        } 
    if bool(image) == False:
        image = None
    if bool(inner_phone) == False:
        inner_phone = None
    if len(group_id) > 0:
        group_id = group_id[0].split(",")
    if len(roles_id) > 0:
        roles_id = roles_id[0].split(",")
    user_request = UserRequest(
        id=id,
        email=email,
        password = password,
        login = login,
        name = name,
        last_name = last_name,
        patronymic = patronymic,
        fio=f"{name} {last_name} {patronymic}".strip(),
        is_operator = is_operator,
        deparment_id = deparment_id,
        position_id = position_id,
        group_id = group_id,
        roles_id = roles_id,
        date_employment_at = date_employment_at,
        phone = phone,
        inner_phone = inner_phone,
        date_dismissal_at = date_dismissal_at,
        image = image,
    )
    user = user_service.update_user(user_request)
    if type(user) == tuple:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": "Bad request"
        }
    return user

@route.delete("/{id}")
@inject
def user_delete(id: int, response: Response, user_service: UserService = Depends(Provide[Container.user_service])):
    try:
        return user_service.delete_user_by_id(id)
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": str(e)
        }

def check_file(image):
    return bool(image) and image.content_type.find("image") == -1
    
    
