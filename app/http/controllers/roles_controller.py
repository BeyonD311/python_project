from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container
from app.http.services.roles import RolesServices, Create, Update
from app.database import NotFoundError
from fastapi.security import HTTPBearer
from sqlalchemy.exc import IntegrityError

security = HTTPBearer()


route = APIRouter(
    prefix="/roles",
    tags=['roles'],
    responses={404: {"description": "Not found"}} 
)


@route.get("/")
@inject
async def get_roles(
    roles_model: RolesServices = Depends(Provide[Container.roles_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    return roles_model.get()

@route.get("/modules")
@inject
async def get_modules(
    roles_model: RolesServices = Depends(Provide[Container.roles_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    return roles_model.get_modules()

@route.get("/{id}")
@inject
async def get_role(
    id: int,
    response: Response,
    roles_model: RolesServices = Depends(Provide[Container.roles_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    try:
        return roles_model.get(id).pop()
    except NotFoundError:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": f"Not found role {id}"
        }

@route.post("/")
@inject
async def create_role(
    params: Create,
    response: Response,
    roles_model: RolesServices = Depends(Provide[Container.roles_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    try:
        return roles_model.create(params)
    except IntegrityError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "message": str(e)
        }
    

@route.put("/")
@inject
async def update_role(
    params: Update,
    response: Response,
    roles_model: RolesServices = Depends(Provide[Container.roles_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    try:
        return roles_model.update(params)
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": str(e)
        }
@route.delete("/{id}")
@inject
async def delete_role(
    id:int,
    response: Response,
    roles_model: RolesServices = Depends(Provide[Container.roles_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        return roles_model.delete(id)
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": "Role not found"
        }