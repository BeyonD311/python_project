from fastapi import APIRouter, Depends, status, Response
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.database import NotFoundError
from app.kernel import Container
from app.http.services.departments import DepartmentsService, DepartmentParams

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
    deparment_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return deparment_service.get_struct()
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(e)
        }