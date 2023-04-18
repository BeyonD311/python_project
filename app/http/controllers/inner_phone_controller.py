import jwt
import os
from fastapi import Depends, APIRouter, Response, status, Request
from fastapi.security import HTTPBearer
from app.kernel.container import Container
from dependency_injector.wiring import Provide, inject
from app.http.services.inner_phone import RequestInnerPhone
from app.http.services.inner_phone import InnerPhoneServices
from app.database.repository import NotFoundError
from app.http.services.helpers import default_error

security = HTTPBearer()

route = APIRouter(
    prefix="/users/inner_phone",
    tags=['users_inner_phone'],
    responses={404: {"description": "Not found"}} 
)

@route.get("/user/{user_id}")
@inject
def get_user_inner_phones(
    user_id: int,
    response: Response,
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    inner_phone_service: InnerPhoneServices = Depends(Provide[Container.inner_phone_service])
):
    try:
        return inner_phone_service.get_by_user_id(user_id=user_id)
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": str(e)
        }

@route.post('/')
@inject
def add_inner_phone(
    params: RequestInnerPhone,
    response: Response,
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    inner_phone_service: InnerPhoneServices = Depends(Provide[Container.inner_phone_service])):
    """ 
        Поле id у inner_phone должно быть 0 при создании, при обновлении текущий id
    """
    try:
        inner_phone_service.add(params)
        return {
            "message": "Phone add"
        }
    except Exception as e:
        err = default_error(e)
        response.status_code = err[0]
        return err[1]

@route.put('/')
@inject
def update_inner_phone(
    params: RequestInnerPhone,
    response: Response,
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    inner_phone_service: InnerPhoneServices = Depends(Provide[Container.inner_phone_service])):
    """ 
        Поле id у inner_phone должно быть 0 при создании, при обновлении текущий id
    """
    try:
        inner_phone_service.update(params)
        return {
            "message": "Phone update"
        }
    except Exception as e:
        err = default_error(e)
        response.status_code = err[0]
        return err[1]

@route.delete('/')
@inject
def delete_inner_phone(
    user_id: str,
    phones_id: str,
    response: Response,
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    inner_phone_service: InnerPhoneServices = Depends(Provide[Container.inner_phone_service])):
    """ ** phones_id - пример phones_id=1,2,3 """
    try:
        inner_phone_service.delete(user_id, phones_id.split(","))
        return {
            "message": "Phone delete"
        }
    except Exception as e:
        err = default_error(e)
        response.status_code = err[0]
        return {
            "message": err[1]
        }


@route.get("/settings")
@inject
def get_settings_by_user_id(
        request: Request,
        response: Response,
        inner_phone_service: InnerPhoneServices = Depends(Provide[Container.inner_phone_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    token = request.headers.get('authorization').replace("Bearer ", "")
    decode = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
    try:
        return inner_phone_service.get_settings_by_user_id(user_id=decode['azp'])
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "message": 'Not found settings for current user.'
        }
