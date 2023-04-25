import re
import json
import jwt
import os
from fastapi import Depends, APIRouter, Response, status, Body, Request, HTTPException
from datetime import datetime
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container
from app.http.services.helpers import default_error
from app.http.services.users import UserService
from app.http.services.users import UserRequest
from app.http.services.users import UsersFilter
from app.http.services.users import UserParams
from app.http.services.departments import DepartmentsService
from app.http.services.groups import GroupsService
from app.http.services.users import SkillService, UserPermission
from app.database import ExpectationError, AccessException
from fastapi.security import HTTPBearer


security = HTTPBearer()

route = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not found"}} 
)


@route.get("/departments")
@inject
async def get_departments(
    departments_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return departments_service.get_all()

@route.get("/departments/{departments_id}")
@inject
async def get_departments_user(
    departments_id: int,
    response: Response,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    '''

    Результат - вывод Супервизоров и руководителя отдела ("head_of_department": true)

     описание полей \n
     - departments_id - id отдела пользователя
    '''
    try:
        result = user_service.get_departments_employees(departments_id)
    except Exception as e:
        err = default_error(e, item='Users Department')
        response.status_code = err[0]
        result = err[1]
    return result

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
    response: Response,
    skill_service: SkillService = Depends(Provide[Container.skill_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    '''

    Результат - вывод пользовательского навыка по его ID.

     описание полей \n
     - skill - id навыка пользователя
    '''
    try:
        result = skill_service.find(skill)
    except Exception as e:
        err = default_error(e, item='Users Skill')
        response.status_code = err[0]
        result = err[1]
    return result

@route.post("/skill")
@inject
def create_user_skill(
    skill: str = Body(),
    skill_service: SkillService = Depends(Provide[Container.skill_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    result = skill_service.add(text=skill)
    return result

@route.get("/", status_code = 200)
@inject
async def get_users(
    response: Response,
    request: Request,
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
        ** filter - должен содержать строку типа fio=Фамилия имя отчество;login=логин пользователя;status=id статуса;
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
        reg = r'([a-z]*)(=)([А-Яа-яa-zA-Z?\s\d\,]*)'
        user_filter = UsersFilter()
        result = re.findall(reg,filter)
        flag = False
        for r in result:
            if r[0] in user_filter.__dict__ and r[2] != "":
                flag = True
                param = r[2]
                if r[0].lower() == "status":
                    param = r[2].split(",")
                user_filter.__setattr__(r[0], param)
        if flag:
            params.filter = user_filter
    try:
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            # TODO: убрать raise
            if request.state.for_user['user'].department_id is None:
                description = f"Запрашиваемый пользователь не состоит ни в одном отделе."
                raise ExpectationError(entity_id='', entity_description=description)
            if params.filter is None:
                params.filter = UsersFilter()
            params.filter.department = request.state.for_user['user'].department_id
            del request.state.for_user['user']
        result = user_service.get_all(params=params)
    except Exception as e:
        err = default_error(e, item='Users')
        response.status_code = err[0]
        result = err[1]
    return result

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
    """ Получение текущего пользователя\n
    Exception:
        NotFoundError
    """
    token = request.headers.get('authorization').replace("Bearer ", "")
    decode = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
    try:
        result = user_service.get_user_by_id(decode['azp'])
    except Exception as e:
        err = default_error(e, item='Users')
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/get_pass")
@inject
async def current_password(
    response: Response,
    request: Request,
    user_id: int = None,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        token = request.headers.get('authorization').replace("Bearer ", "")
        if user_id == None:  # NOTE: Get own password
            decode = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            user_id = decode['azp']
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            request.state.for_user['user']
            if request.state.for_user['user'].id != user_id:
                raise AccessException(entity_id=user_id)
            del request.state.for_user['user']
        current = user_service.by_id(user_id)
        result = {
            "id": user_id,
            "password": current.password
        }
    except Exception as e:
        err = default_error(e, item='Users')
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/{id}")
@inject
async def get_user_id(
    id: int, 
    response: Response,
    request: Request,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    try:
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            slef_id = request.state.for_user['user'].id
            if slef_id != id:
                raise AccessException(entity_id=slef_id)
        result = user_service.get_user_by_id(id, False)
    except Exception as e:
        err = default_error(e, item='Users')
        response.status_code = err[0]
        result = err[1]
    return result

@route.post("/")
@inject
async def add_user(
    response: Response,
    user_request: UserRequest = Body(),
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    try:
        user = await user_service.create_user(user_request)
        await user_service.set_status(user.id,user.status.status_id)
        result = user
    except Exception as e:
        err = default_error(e, item='Users')
        response.status_code = err[0]
        result = err[1]
    return result


@route.patch("/permissions")
@inject
async def user_set_permission(
    response: Response, 
    request: Request, 
    params: UserPermission,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            slef_id = request.state.for_user['user'].id
            if slef_id != id:
                raise AccessException(entity_id=slef_id)
        result = user_service.set_permission(params)
    except Exception as e:
        # TODO: response.status_code = status.HTTP_404_NOT_FOUND, "message": "Not found status"
        err = default_error(e, item='Users Permission')
        response.status_code = err[0]
        result = err[1]
    return result

@route.patch("/update_password/{id}")
@inject
async def update_password(
    id: int,
    password: str,
    request: Request,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    if hasattr(request.state,'for_user') and request.state.for_user['status']:
        slef_id = request.state.for_user['user'].id
        if slef_id != id:
            raise AccessException(entity_id=slef_id)
    return user_service.reset_password(id, password)

@route.patch("/dismiss")
@inject
async def user_dismiss(
        response: Response, 
        id: int = Body(), 
        date_dismissal_at: datetime = Body(default=None),
        user_service: UserService = Depends(Provide[Container.user_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """
        **date_dismissal_at** - формат времени (yyyy-mm-dd hh:mm:dd)
    """
    try:
        return user_service.dismiss(id, date_dismissal_at)
    except Exception as e:
        err = default_error(e, item='Users')
        response.status_code = err[0]
        result = err[1]
    return result

@route.patch("/recover/{id}")
@inject
async def user_dismiss(
        response: Response, 
        id: int, 
        request: Request,
        user_service: UserService = Depends(Provide[Container.user_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            slef_id = request.state.for_user['user'].id
            if slef_id != id:
                raise AccessException(entity_id=slef_id)
        result = user_service.recover(id)
        await user_service.set_status(id,status_id=1)
    except Exception as e:
        description = f"Пользователя с ID={id} не существует."
        err = default_error(e, item='Users')
        response.status_code = err[0]
        result = err[1]
    return result

@route.put("/{id}")
@inject
async def update_user(
    id: int,
    response: Response,
    request: Request,
    params: UserRequest = Body(),
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    try:
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            slef_id = request.state.for_user['user'].id
            if slef_id != id:
                raise AccessException(entity_id=slef_id)
        user = user_service.update_user(id, params)
        return user
    except Exception as e:
        description = f"Пользователя с ID={id} не существует."
        err = default_error(e, item='Users')
        response.status_code = err[0]
        result = err[1]
    return result
    
@route.delete("/{id}")
@inject
async def user_delete(id: int, response: Response,request: Request, user_service: UserService = Depends(Provide[Container.user_service]),HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            slef_id = request.state.for_user['user'].id
            if slef_id != id:
                raise AccessException(entity_id=slef_id)
        user_service.delete_user_by_id(id)
        description = "Пользователь с ID={id} успешно удалён."
        result = {
            "message": f"User is deleted {id}",
            "description": description
        }
    except Exception as e:
        description = f"Пользователя с ID={id} не существует."
        err = default_error(e, item='Users')
        response.status_code = err[0]
        result = err[1]
    return result
