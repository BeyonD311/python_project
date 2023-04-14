import jwt, os, json, logging
from websockets.exceptions import ConnectionClosedError
from fastapi import Depends, APIRouter, Response, Request, WebSocket
from fastapi.security import HTTPBearer
from app.kernel.container import Container
from dependency_injector.wiring import Provide, inject
from app.http.services.users import UserService
from app.http.services.helpers import default_error

security = HTTPBearer()

route = APIRouter(
    prefix="/users/status",
    tags=['status'],
    responses={404: {"description": "Not found"}} 
)

@route.get("/all")
@inject
async def get_all_status(
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    return user_service.get_all_status_users()

@route.get("/")
@inject
async def current_user_status(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """ 
        long polling - для статусов \n
        **user_id - принимает в себя id пользователей через запятую пример "1,2,3"
    """
    users: list = user_id.split(",")
    statuses = await user_service.get_users_status(users_id=users)

    return statuses

@route.patch("/")
@inject
async def update_status(
    status_id: int, 
    response: Response, 
    request: Request, 
    user_id: int = None,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """ Если параметр '**user_id** == null' то будет изменен статус текущего пользователя """
    try:
        if user_id == None:
            token = request.headers.get('authorization').replace("Bearer ", "")
            decode = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            user_id = decode['azp']
        
        await user_service.set_status(user_id,status_id=status_id)
        return {
            "message": "set status"
        }
    except Exception as e:
        err = default_error(e)
        response.status_code = err[0]
        return {
            "message": err[1]
        }
    
@route.get("/asterisk")
@inject
async def update_status_asterisk(
    status_cod: str, 
    uuid: str,
    status_time: int,
    response: Response, 
    request: Request, 
    caller: str = None,
    user_service: UserService = Depends(Provide[Container.user_service])):
    """ 
        **status_cod** - код статуса\n
        **uuid** - uuid пользователя\n
        **status_time** - время установки статуса 
    """
    try:
        await user_service.set_status_by_aster(uuid=uuid, status_code=status_cod, status_time=status_time, incoming_call=caller)
        return {
            "message": "set status"
        }
    except Exception as e:
        err = default_error(e)
        response.status_code = err[0]
        return {
            "message": err[1]
        }

@route.websocket("/ws")
@inject
async def ws_channel_user_status(
    websocket: WebSocket,
    user_service: UserService = Depends(Provide[Container.user_service])
):
    await websocket.accept()
    try:
        while True:
            incoming_data = await websocket.receive_json()
            if 'user_id' not in incoming_data:
                raise ConnectionClosedError(rcvd="Пользователь не найден",sent="Close")
            if bool(incoming_data['user_id']) == False:
                raise ConnectionClosedError(rcvd="Пользователь не найден",sent="Close")
            await user_service.redis_pub_sub(websocket, incoming_data['user_id'])
    except json.decoder.JSONDecodeError as decode_exception:
        await websocket.send_json({
            "status": "fail",
            "data": [],
            "message": "Данные не обнаружены"
        })
    except ConnectionClosedError as connect_close:
        await websocket.send_json({
            "status": "fail",
            "data": [],
            "message": "Данные не обнаружены "
        })