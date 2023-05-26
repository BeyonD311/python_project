from fastapi import Depends, APIRouter, Response
from fastapi.security import HTTPBearer
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container
from app.http.services.departments import DepartmentsService
from app.http.services.users import UserService
from app.exceptions import exceptions_handling

security = HTTPBearer()

route = APIRouter(
    prefix="/users/departments",
    tags=['users'],
    responses={404: {"description": "Not found"}} 
)

@route.get("")
@inject
async def get_departments(
    departments_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):

    """ Получение всех отделов доступных для пользователя """

    return departments_service.get_all()

@route.get("/{departments_id}")
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
    except Exception as exception:
        result exceptions_handling(exception)
    return result