from fastapi import APIRouter, Depends, status, Response
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.http.services.helpers import parse_params_num
from app.kernel import Container
from app.http.services.departments import (DepartmentsService, DepartmentParams, Filter, FilterParams)
from app.http.services.helpers import default_error

route = APIRouter(
    prefix="/department",
    tags=['department'],
    responses={404: {"description": "Not found"}} 
)

security = HTTPBearer()

@route.get("/")
@inject
def get_departments(
    response: Response,
    fio: str = None,
    department: str = "",
    position: str = "",
    status: str = "",
    phone: str = None,
    department_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """ 
    Получение отделов и сотрудников \n
    **fio: str,\n
    **department: str = пример "1,2,3" ввод id через запятую,
    **position: str = пример "1,2,3" ввод id через запятую,
    **status: str = пример "1,2,3" ввод id через запятую,
    **phone: str,
     """
    try:
        department = parse_params_num(department)
        position = parse_params_num(position)
        status = parse_params_num(status)
        filter_params = {
            "fio": fio,
            "department": department,
            "position": position,
            "status": status,
            "phone": phone
        }
        filter_params = Filter(**filter_params)
        result = department_service.get_employees(filter_params)
    except Exception as e:
        err = default_error(e, source='Departments')
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/filter", response_model=FilterParams)
@inject
def get_filter_params_departments(
    department_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """ Получение данных для полей фильрации \n """
    return department_service.get_filter_params()


@route.post("/")
@inject
def add_department(
    params: DepartmentParams,
    response: Response,
    department_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """
    Exceptions:
        ExistsException
    """
    try:
        result = department_service.add(params=params)
    except Exception as e:
        err = default_error(e, source='Departments')
        response.status_code = err[0]
        result = err[1]
    return result

@route.put("/{id}")
@inject
def update_department(
    id: int,
    params: DepartmentParams,
    response: Response,
    department_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """
    Exceptions:
        NotFoundError
    """
    try:
        result = department_service.update(params=params, id=id)
    except Exception as e:
        err = default_error(e, source='Departments')
        response.status_code = err[0]
        result = err[1]
    return result

@route.delete("/{id}")
@inject
def delete_department(
    id: int,
    response: Response,
    department_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """
    Exceptions:
        NotFoundError
    """
    try:
        result = department_service.delete(id)
    except Exception as e:
        err = default_error(e, source='Departments')
        response.status_code = err[0]
        result = err[1]
    return result
