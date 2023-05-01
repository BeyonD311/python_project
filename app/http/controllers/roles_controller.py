from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container
from app.http.services.roles import RolesServices, Create, Update
from app.http.services.helpers import default_error
from app.database import NotFoundError, RequestException
from fastapi.security import HTTPBearer

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
        return roles_model.get(id)
    except Exception as e:
        err = default_error(e, source='Role')
        response.status_code = err[0]
        result = err[1]
    return result

@route.post("/")
@inject
async def create_role(
    params: Create,
    response: Response,
    roles_model: RolesServices = Depends(Provide[Container.roles_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    try:
        result = roles_model.create(params)
    except Exception as e:
        err = default_error(e, source='Role')
        response.status_code = err[0]
        result = err[1]
    return result
    

@route.put("/")
@inject
async def update_role(
    params: Update,
    response: Response,
    roles_model: RolesServices = Depends(Provide[Container.roles_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
    ):
    try:
        result = roles_model.update(params)
    except Exception as e:
        err = default_error(e, source='Role')
        response.status_code = err[0]
        result = err[1]
    return result

@route.delete("/{id}")
@inject
async def delete_role(
    id:int,
    response: Response,
    roles_model: RolesServices = Depends(Provide[Container.roles_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        result = roles_model.delete(id)
    except Exception as e:
        err = default_error(e, source='Roles')
        response.status_code = err[0]
        result = err[1]
    return result
