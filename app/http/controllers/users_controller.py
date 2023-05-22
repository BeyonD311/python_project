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
from pydantic import ValidationError


security = HTTPBearer()

route = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not found"}} 
)

@route.get("/fill", include_in_schema=False)
@inject
async def fill_redis(
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    await user_service.all()

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
        err = default_error(e, source='Users Department')
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
        err = default_error(e, source='Users Skill')
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
    try:
        if filter is not None:
            user_filter = {}
            filter = filter.split(";")
            for filter_param in filter:
                params_filter = filter_param.split("=")
                if len(params_filter) > 1:
                    if params_filter[0] == "status":
                        params_filter[1] = params_filter[1].split(",")
                    user_filter[params_filter[0]] = params_filter[1]
            params.filter = UsersFilter(**user_filter)
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            if request.state.for_user['user'].department_id is None:
                # TODO: проверить исключение и корректность description
                description = f"Запрашиваемый пользователь не состоит ни в одном отделе."
                raise ExpectationError(entity_description=description)
            if params.filter is None:
                params.filter = UsersFilter()
            params.filter.department = request.state.for_user['user'].department_id
            del request.state.for_user['user']
        result = user_service.get_all(params=params)
    except ValidationError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return e.errors()
    except Exception as e:
        err = default_error(e, source='Users')
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
    Exceptions:
        NotFoundError
    """
    try:
        result = user_service.get_user_by_id(request.state.current_user_id)
    except Exception as e:
        err = default_error(e, source='Users')
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
    """ Получение пароля текущего пользователя\n
    Exceptions:
        AccessException
    """
    try:
        if user_id == None:  # NOTE: Get own password
            user_id = request.state.current_user_id
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            request.state.for_user['user']
            if request.state.for_user['user'].id != user_id:
                # TODO проверить исключение
                description: str = "Недостаточно прав доступа."
                raise AccessException(entity_id=user_id, entity_description=description)
            del request.state.for_user['user']
        current = user_service.by_id(user_id)
        result = {
            "id": user_id,
            "password": current.password
        }
    except Exception as e:
        err = default_error(e, source='Users')
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
    """ Получение пользователя по id.\n
    Exceptions:
        NotFoundError
    """
    try:
        if id == 0:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {
                "description": f"Не найден пользователь ID={0}"
            }
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            slef_id = request.state.for_user['user'].id
            if slef_id != id:
                description: str = "Недостаточно прав доступа."
                raise AccessException(entity_id=slef_id, entity_description=description)
        result = user_service.get_user_by_id(id, False)
    except Exception as e:
        err = default_error(e, source='Users')
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
    """ Создание пользователя\n
    Exceptions:
        NotFoundError
    """
    try:
        user = await user_service.create_user(user_request)
        await user_service.set_status(user.id,user.status.status_id)
        result = user
    except Exception as e:
        err = default_error(e, source='Users')
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
    """ Изменить уровни доступа пользователя\n
    Exceptions:
        NotFoundError
        AccessException
    """
    try:
        if hasattr(request.state,'for_user') and request.state.for_user['status']:
            slef_id = request.state.for_user['user'].id
            if slef_id != id:
                # TODO проверить исключение
                description: str = "Недостаточно прав доступа."
                raise AccessException(entity_id=slef_id,entity_message="123",entity_description=description)
        result = user_service.set_permission(params)
    except Exception as e:
        err = default_error(e, source='Users Permission')
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
    """ Изменить пароль пользователя\n
    Exceptions:
        NotFoundError
        AccessException
    """
    if hasattr(request.state,'for_user') and request.state.for_user['status']:
        slef_id = request.state.for_user['user'].id
        if slef_id != id:
            # TODO проверить исключение
            description: str = "Недостаточно прав доступа."
            raise AccessException(entity_id=slef_id, entity_description=description)
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
        err = default_error(e, source='Users')
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
                # TODO проверить исключение
                description: str = "Недостаточно прав доступа."
                raise AccessException(entity_id=slef_id, entity_description=description)
        result = user_service.recover(id)
        await user_service.set_status(id,status_id=15)
    except Exception as e:
        description = f"Пользователя с ID={id} не существует."
        err = default_error(e, source='Users')
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
                description: str = "Недостаточно прав доступа."
                raise AccessException(entity_id=slef_id, entity_description=description)
        # TODO: Отловить 422 Error: Unprocessable Entity ("msg": "value is not a valid type", "type": "type_error")
        result = user_service.update_user(id, params)
    except Exception as e:
        description = f"Пользователя с ID={id} не существует."
        err = default_error(e, source='Users')
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
                description: str = "Недостаточно прав доступа."
                raise AccessException(entity_id=slef_id, entity_description=description)
        user_service.delete_user_by_id(id)
        description = "Пользователь с ID={id} успешно удалён."
        result = {
            "message": f"User is deleted {id}",
            "description": description
        }
    except Exception as e:
        description = f"Пользователя с ID={id} не существует."
        err = default_error(e, source='Users')
        response.status_code = err[0]
        result = err[1]
    return result
