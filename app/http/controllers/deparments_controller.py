from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.database import NotFoundError
from app.kernel import Container
from app.http.services.departments import DepartmentsService, DepartmentParams

route = APIRouter(
    prefix="/deparment",
    tags=['deparment'],
    responses={404: {"description": "Not found"}} 
)

security = HTTPBearer()

@route.get("/")
@inject
def get_employees(
    deparment_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    pass

@route.post("/")
@inject
def add_employees(
    params: DepartmentParams,
    deparment_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    deparment_service.add(params=params)