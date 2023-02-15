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

@route.get("/{id}")
@inject
def get_deparments(
    id: int,
    response: Response,
    deparment_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return deparment_service.get_by_id(id)
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(e)
        }

@route.post("/")
@inject
def add_deparment(
    params: DepartmentParams,
    response: Response,
    deparment_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return deparment_service.add(params=params)
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(e)
        }

@route.put("/{id}")
@inject
def update_deparment(
    id: int,
    params: DepartmentParams,
    response: Response,
    deparment_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return deparment_service.update(params=params, id=id)
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(e)
        }

@route.delete("/{id}")
@inject
def delete_deparment(
    id:int,
    response: Response,
    deparment_service: DepartmentsService = Depends(Provide[Container.department_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return     deparment_service.delete(id)
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(e)
        }