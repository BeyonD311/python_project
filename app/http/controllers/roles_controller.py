from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container
from app.http.services import RolesServices

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
    return roles_model.get_all()