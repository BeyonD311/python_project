import re
import json
import jwt
import os
from fastapi import Depends, APIRouter, Response, status, Body, Request, HTTPException
from datetime import datetime
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container
from app.http.services.users import UserService
from app.http.services.users import UserRequest
from app.http.services.users import UsersFilter
from app.http.services.users import UserParams
from app.http.services.departments import DepartmentsService
from app.http.services.groups import GroupsService
from app.http.services.users import SkillService, UserPermission
from app.database import NotFoundError
from fastapi.security import HTTPBearer
from sqlalchemy.exc import IntegrityError

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

     описание полея \n
     - departments_id - id отдела пользователя 
    '''

    try:
        if departments_id == 0:
            raise NotFoundError(departments_id)
        return user_service.get_departments_employees(departments_id)
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_404_NOT_FOUND
        description = "Отдел с таким ID не найден."
        return {
            "status": "fail",
            "message": "Not found departments",
            "description": description
        }

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
def create_user_skill(
    skill: str = Body(),
    skill_service: SkillService = Depends(Provide[Container.skill_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return skill_service.add(text=skill)

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
        ** fileter - должен содержать строку типа fio=Фамилия имя отчество;login=логин пользователя;status=id статуса;
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
    if hasattr(request.state,'for_user') and request.state.for_user['status']:
        if request.state.for_user['user'].department_id is None:
            response.status_code = status.HTTP_417_EXPECTATION_FAILED
            description = f"Запрашиваемый пользователь не состоит ни в одном отделе."
            return {
                "status": "fail",
                "message": "User Not found department",
                "description": description
            }
        if params.filter is None:
            params.filter = UsersFilter()
        params.filter.department = request.state.for_user['user'].department_id
        del request.state.for_user['user']
    return user_service.get_all(params=params) 

@route.get("/position")
@inject
async def user_position(
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return user_service.get_user_position()

@route.get("/current")
@inject
async def current_user(
    request: Request, 
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """ Получение текущего пользователя """
    token = request.headers.get('authorization').replace("Bearer ", "")
    decode = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
    current = user_service.get_user_by_id(decode['azp'])
    return current

@route.get("/get_pass")
@inject
async def current_password(
    response: Response, 
    request: Request, 
    user_id: int = None,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        if user_id == 0:
            response.status_code = status.HTTP_404_NOT_FOUND
            return 
        if user_id == None:
            token = request.headers.get('authorization').replace("Bearer ", "")
            decode = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            user_id = decode['azp']
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            request.state.for_user['user']
            if request.state.for_user['user'].id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource not available")
            del request.state.for_user['user']
        current = user_service.by_id(user_id)
        return {
            "id": user_id,
            "password": current.password
        }
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        description = f"Пользователя с ID={user_id} не существует."
        return {
            "message": str(e),
            "description": description
        }
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
        if id == 0:
            raise NotFoundError(id)
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            if request.state.for_user['user'].id != id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource not available")
        return user_service.get_user_by_id(id, False)
    except NotFoundError as e:
        print(e)
        response.status_code = status.HTTP_404_NOT_FOUND
        description = f"Пользователя с ID={id} не существует."
        return {
            "status": "fail",
            "message": "Not found user",
            "description": description
        }

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
        if type(user) == tuple:
            response.status_code = status.HTTP_400_BAD_REQUEST
            description = "Неверный запрос."
            return {
                "message": "Bad request",
                "description": description
            }
        await user_service.set_status(user.id,user.status.status_id)
        return user
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        description = ""
        return {
            "message": str(e),
            "description": description
        }
    except IntegrityError as e:
        errorInfo = e.orig.args
        response.status_code = status.HTTP_400_BAD_REQUEST
        pattern = r'(DETAIL:(?:[^\\\n]*))'
        match = re.findall(pattern=pattern, string=errorInfo[0])
        # if re.search(pattern="already exists", string=match[0]):
        #     pattern = r'(?<=\()[\w_@.,]+(?=.*\))'
        #     field, value, *_ = re.findall(pattern=pattern, string=match[0])
        #     description = f"Пользователь со значением '{value}' в поле '{field}' уже существует."
        # else:
        #     description = f"Неверно заполнено поле: {errorInfo}"
        description = f"Неверно заполнено поле"
        return {
            "message": match[0],
            "description": description
        }

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
            if request.state.for_user['user'].id != id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource not available")
        return user_service.set_permission(params)
    except IntegrityError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        description = ""
        return {
            "message": "Not found status",
            "description": description
        }

@route.patch("/update_password/{id}")
@inject
async def update_password(
    id: int,
    password: str,
    request: Request,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    if hasattr(request.state,'for_user') and request.state.for_user['status']:
        if request.state.for_user['user'].id != id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource not available")
    return user_service.reset_password(id, password)

@route.patch("/dismiss")
@inject
async def user_dismiss(
        response: Response, 
        id: int = Body(), 
        date_dismissal_at: datetime = Body(default=None),
        user_service: UserService = Depends(Provide[Container.user_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        """ 
            **date_dismissal_at** - формат времени (yyyy-mm-dd hh:mm:dd)
        """
        return user_service.dismiss(id, date_dismissal_at)
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        description = ""
        return {
            "message": str(e),
            "description": description
        }

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
            if request.state.for_user['user'].id != id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource not available")
        Res = user_service.recover(id)
        await user_service.set_status(id,status_id=1)
        return Res
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        description = ""
        return {
            "message": str(e),
            "description": description
        }

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
            if request.state.for_user['user'].id != id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource not available")
        user = user_service.update_user(id, params)
        return user
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        description = ""
        return {
            "message": str(e),
            "description": description
        }
    
@route.delete("/{id}")
@inject
async def user_delete(id: int, response: Response,request: Request, user_service: UserService = Depends(Provide[Container.user_service]),HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            if request.state.for_user['user'].id != id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource not available")
        user_service.delete_user_by_id(id)
        description = ""
        return {
            "message": f"User is delete {id}",
            "description": description
        }
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        description = ""
        return {
            "message": str(e),
            "description": description
        }
