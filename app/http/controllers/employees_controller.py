""" from fastapi import APIRouter, Depends, status, Response
from app.http.services.helpers import parse_params_num
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.database import NotFoundError
from app.kernel import Container
from app.http.services.departments import DepartmentsService

route = APIRouter(
    prefix="/employees",
    tags=['employees'],
    responses={404: {"description": "Not found"}} 
)

security = HTTPBearer()

@route.get("/")
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
        } """