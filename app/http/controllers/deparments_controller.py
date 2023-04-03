from fastapi import APIRouter, Depends, status, Response
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.http.services.helpers import parse_params_num
from app.database import NotFoundError
from app.kernel import Container
from app.http.services.departments import DepartmentsService, DepartmentParams
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
        return department_service.get_employees(filter_params)
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(e)
        }

@route.get("/employees")
@inject
def get_employees(
    response: Response,
    fio: str = None,
    department: str = "",
    position: int = "",
    status: int = "",
    phone: str = None,
    page: int = 1,
    limit: int = 10,
    department_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
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
        return department_service.get_users_department(filter_params, page, limit)
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(e)
        }

@route.post("/")
@inject
def add_department(
    params: DepartmentParams,
    response: Response,
    department_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return department_service.add(params=params)
    except Exception as e:
        res = default_error(e)
        response.status_code = res[0]
        return res[1]

@route.put("/{id}")
@inject
def update_department(
    id: int,
    params: DepartmentParams,
    response: Response,
    department_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return department_service.update(params=params, id=id)
    except Exception as e:
        res = default_error(e)
        response.status_code = res[0]
        return res[1]

@route.delete("/{id}")
@inject
def delete_department(
    id:int,
    response: Response,
    department_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return     department_service.delete(id)
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(e)
        }