import re
import jwt
import os
import copy
from fastapi import Depends, APIRouter, Response, status, UploadFile, Body, File, Request
from typing import List
from datetime import datetime
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container
from app.http.services import UserService, UserRequest, UsersFilter, UserParams, DepartmentsService, GroupsService, SkillService
from app.database import NotFoundError
from fastapi.security import HTTPBearer
from sqlalchemy.exc import IntegrityError

security = HTTPBearer()

route = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not found"}} 
)

@route.get("/deparments")
@inject
async def get_deparments(
    depratments_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return depratments_service.get_all()

@route.get("/groups")
@inject
def get_all_groups(
    groups_service: GroupsService = Depends(Provide[Container.groups_repository]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return groups_service.get_all() 

@route.get("/skill")
@inject
def get_user_skill(
    skill: str,
    skill_service: SkillService = Depends(Provide[Container.skill_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return skill_service.find(skill)

@route.post("/skill")
@inject
def get_user_skill(
    skill: str = Body(),
    skill_service: SkillService = Depends(Provide[Container.skill_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return skill_service.add(text=skill)

@route.get("/", status_code = 200)
@inject
async def get_users(
    response: Response,
    page: int = 1,
    size: int = 10,
    sort_field: str = 'id',
    sort_dir: str = 'asc',
    filter: str = None,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    """ 
    описание полей \n
        ** fileter - должен содержать строку типа fio=Фамилия имя отчестов;login=логин пользователя;status=id статуса;
     """
    
    if page == 1 or page <= 0:
        page = 0
    else:
        page = page - 1
    params = UserParams(
        page=page,
        size=size,
        sort_field=sort_field,
        sort_dir=sort_dir
    )
    if filter is not None:
        reg = r'([a-z]*)(=)([А-Яа-яa-zA-Z?\s\d]*)'
        user_filter = UsersFilter()
        result = re.findall(reg,filter) 
        flag = False
        for r in result:
            if r[0] in user_filter.__dict__ and r[2] != "":
                flag = True
                user_filter.__setattr__(r[0], r[2])
        if flag:
            params.filter = user_filter
    try: 
        return user_service.get_all(params=params) 
    except Exception as e:
        response.status_code = status.HTTP_417_EXPECTATION_FAILED
        return {
            "status": "fail",
            "message": str(e)
        }

@route.get("/status_all")
@inject
async def current_user(
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return user_service.get_all_status_users()

@route.get("/position")
@inject
async def user_position(
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return user_service.get_user_position()

@route.get("/current")
@inject
async def current_user(
    response: Response, 
    request: Request, 
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """ Получение текущего пользователя """
    token = request.headers.get('authorization').replace("Bearer ", "")
    decode = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
    current = user_service.get_user_by_id(decode['azp'])
    for role in current.roles:
        role.permissions
    return copy(current)

@route.get("/get_pass")
@inject
async def current_user(
    response: Response, 
    request: Request, 
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    token = request.headers.get('authorization').replace("Bearer ", "")
    decode = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
    current = user_service.get_user_by_id(decode['azp'], True)
    return current.password

@route.get("/{id}")
@inject
async def get_user_id(
    id: int, 
    response: Response,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    
    try:
        if id == 0:
            raise NotFoundError(id)
        user = user_service.get_user_by_id(id)
        return copy(user)
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
    deparment_id: List[str] = Body(default=None),
    position_id: int = Body(), 
    group_id: List[str] = Body(),
    roles_id: List[str] = Body(),
    skills_id: List[str] = Body(default=None),
    date_employment_at: datetime = Body(default=datetime.now()),
    phone: str = Body(default=None),
    inner_phone: int|str = Body(default=None),
    image: UploadFile = File(default=None),
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    if bool(image) == False:
        image = None
    if bool(inner_phone) == False:
        inner_phone = None
    if bool(date_dismissal_at) == False:
        date_dismissal_at = None
    if len(group_id) > 0:
        group_id = group_id[0].split(",")
    if len(roles_id) > 0:
        roles_id = roles_id[0].split(",")
    if len(skills_id) > 0 and skills_id[0] != '':
        skills_id = skills_id[0].split(",")
    else:
        skills_id = []
    if len(deparment_id) > 0 and deparment_id[0] != '':
        deparment_id = deparment_id[0].split(",")
    else:
        deparment_id = []
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
        skills_id= skills_id,
        date_employment_at = date_employment_at,
        phone = phone,
        inner_phone = inner_phone,
        date_dismissal_at = date_dismissal_at,
        image = image,
    )
    try:
        user = user_service.create_user(user_request)
        if type(user) == tuple:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "message": "Bad request"
            }
        return user
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": str(e)
        }

@route.patch("/status")
@inject
async def update_status(
    status_id: int, 
    response: Response, 
    request: Request, 
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        token = request.headers.get('authorization').replace("Bearer ", "")
        decode = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
        user_service.set_status(decode['azp'],status_id=status_id)
        return {
            "message": "set status"
        }
    except IntegrityError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": "Not found status"
        }

@route.patch("/update_password/{id}")
@inject
async def update_password(
    id: int,
    password: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):

   return user_service.reset_password(id, password)


@route.put("/{id}")
@inject
async def update_user(
    id: int,
    response: Response,
    email: str = Body(),
    password: str = Body(),
    name: str = Body(),
    last_name: str = Body(),
    patronymic: str = Body(default=None),
    login: str = Body(),
    is_operator: bool = Body(default=False),
    deparment_id: List[str] = Body(default=None),
    position_id: int = Body(),
    group_id: List[str] = Body(),
    roles_id: List[str] = Body(),
    skills_id: List[str] = Body(default=None),
    date_employment_at: datetime = Body(default=datetime.now()),
    phone: str = Body(default=None),
    inner_phone: int|str = Body(default=None),
    image_id: int = Body(),
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    if bool(image) == False:
        image = None
    if bool(inner_phone) == False:
        inner_phone = None
    if bool(date_dismissal_at) == False:
        date_dismissal_at = None
    if len(group_id) > 0:
        group_id = group_id[0].split(",")
    if len(roles_id) > 0:
        roles_id = roles_id[0].split(",")
    if len(skills_id) > 0 and skills_id[0] != '':
        skills_id = skills_id[0].split(",")
    else:
        skills_id = []
    if len(deparment_id) > 0 and deparment_id[0] != '':
        deparment_id = deparment_id[0].split(",")
    else:
        deparment_id = []
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
        skills_id= skills_id,
        date_employment_at = date_employment_at,
        phone = phone,
        inner_phone = inner_phone,
        date_dismissal_at = date_dismissal_at,
        image = image,
    )
    try:
        user = user_service.update_user(user_request)
        if type(user) == tuple:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "message": "Bad request"
            }
        return user
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": str(e)
        }
    
@route.delete("/{id}")
@inject
def user_delete(id: int, response: Response, user_service: UserService = Depends(Provide[Container.user_service]),HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return user_service.delete_user_by_id(id)
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": str(e)
        }
    
@route.delete("/dismiss/{id}")
@inject
def user_dismiss(
        id: int, 
        response: Response, 
        date_dismissal_at: datetime|str = Body(default=None),

        user_service: UserService = Depends(Provide[Container.user_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        user_service.dismiss(id, date_dismissal_at)
        return {
            "message": "Employee dismiss"
        }
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": str(e)
        }

def copy(user, show_pass: False = False) -> dict:
    res = {}

    for p in user.__dict__:
        if p == "_sa_instance_state":
            continue
        if p == "hashed_password":
            continue
        if show_pass == False and p == "password":
            res[p] = re.sub(r'.*', "*", user.__dict__[p])
        else:
            res[p] = user.__dict__[p]
    
    return res
    
