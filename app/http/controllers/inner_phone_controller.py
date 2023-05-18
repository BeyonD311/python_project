import jwt
import os
from fastapi import Depends, APIRouter, Response, status, Request
from fastapi.security import HTTPBearer
from app.kernel.container import Container
from dependency_injector.wiring import Provide, inject
from app.http.services.inner_phone import RequestInnerPhone
from app.http.services.inner_phone import InnerPhoneServices
from app.http.services.helpers import default_error

from sqlalchemy.exc import IntegrityError

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
    """
    Exceptions:
        NotFoundError
    """
    try:
        result = inner_phone_service.get_by_user_id(user_id=user_id)
    except Exception as e:
        err = default_error(e, source='InnerPhone')
        response.status_code = err[0]
        result = err[1]
    return result

@route.post('/')
@inject
def add_inner_phone(
    params: RequestInnerPhone,
    response: Response,
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    inner_phone_service: InnerPhoneServices = Depends(Provide[Container.inner_phone_service])):
    """
        Поле id у inner_phone должно быть 0 при создании, при обновлении текущего id\n
    Exceptions:
        NotFoundError
        ExistsException
    """
    try:
        if params.inner_phones.id <= 0:
            params.inner_phones.id = 0
        inner_phone_service.add(params)  # TODO: создаёт запись с одинаковым внут.номером
        result =  {
            "message": "Phone added",
            "description": "Внутренний номер успешно добавлен."
        }
    except Exception as e:
        err = default_error(e, source='InnerPhone')
        response.status_code = err[0]
        result = err[1]
    return result

@route.put('/')
@inject
def update_inner_phone(
    params: RequestInnerPhone,
    response: Response,
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    inner_phone_service: InnerPhoneServices = Depends(Provide[Container.inner_phone_service])):
    """ 
        Поле id у inner_phone должно быть 0 при создании, при обновлении текущий id\n
    Exceptions:
        NotFoundError
    """
    try:
        if params.inner_phones.id <= 0:
            params.inner_phones.id = 0
        inner_phone_service.update(params)
        result = {
            "message": "Phone has been updated.",
            "description": "Внутренний номер успешно обновлён."
        }
    except Exception as e:
        err = default_error(e, source='InnerPhone')
        response.status_code = err[0]
        result = err[1]
    return result

@route.delete('/')
@inject
def delete_inner_phone(
    user_id: str,
    phones_id: str,
    response: Response,
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    inner_phone_service: InnerPhoneServices = Depends(Provide[Container.inner_phone_service])):
    """ ** phones_id - пример phones_id=1,2,3\n
    Exceptions:
        NotFoundError
    """
    try:
        inner_phone_service.delete(user_id, phones_id.split(","))
        result = {
            "message": "Phone has been deleted",
            "description": "Внутренний номер успешно удалён."
        }
    except Exception as e:
        err = default_error(e, source='InnerPhone')
        response.status_code = err[0]
        result = {
            "message": err[1]
        }
    return result


@route.get("/settings")
@inject
def get_settings_by_user_id(
        request: Request,
        response: Response,
        inner_phone_service: InnerPhoneServices = Depends(Provide[Container.inner_phone_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    """
    Exceptions:
        NotFoundError
    """
    try:
        result = inner_phone_service.get_settings_by_user_id(user_id=request.state.current_user_id)
    except Exception as e:
        err = default_error(e, source='InnerPhone')
        response.status_code = err[0]
        result = err[1]
    return result
