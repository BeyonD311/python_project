import jwt, os, asyncio
from fastapi import Depends, APIRouter, Response, Request, WebSocket, WebSocketException
from fastapi.security import HTTPBearer
from app.kernel.container import Container
from dependency_injector.wiring import Provide, inject
from app.http.services.users import UserService
from app.http.services.helpers import default_error
from app.http.services.logger_default import get_logger
from app.http.services.sutecrm import Events,send_call_post, send_call_patch


log = get_logger("status_controller.log")

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

@route.get("")
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

@route.patch("")
@inject
async def update_status(
    status_id: int, 
    response: Response, 
    request: Request, 
    user_id: int = None,
    call_id: str = None,
    user_service: UserService = Depends(Provide[Container.user_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """ Если параметр '**user_id** == null' то будет изменен статус текущего пользователя """
    try:
        
        if user_id == None:
            user_id = request.state.current_user_id
        await user_service.set_status(user_id, status_id=status_id, call_id=call_id)
        if status_id == 17 and call_id is not None:
            params = user_service.get_call_by_call_id(call_id)
            await send_call_patch(call_id, params['disposition'], params['billsec'], params['files'])
            await user_service.push_filename_asterisk(params['files'], params['calldate'])
        result = {
            "message": "set status",
            "description": f"Новый статус ID={status_id} установлен."
        }
    except Exception as e:
        err = default_error(e, source='UserService')
        response.status_code = err[0]
        result = {
            "message": err[1]
        }
    return result

@route.get("/asterisk",  include_in_schema=True)
@inject
async def update_status_asterisk(
    status_cod: str, 
    uuid: str,
    status_time: int,
    response: Response, 
    request: Request, 
    caller: str = None,
    call_id: str = None,
    script_ivr_hyperscript: str = None,
    user_service: UserService = Depends(Provide[Container.user_service])):
    """ 
        **status_cod** - код статуса\n
        **uuid** - uuid пользователя\n
        **status_time** - время установки статуса 
    """
    try:
        log.debug(f"Input params: status_cod = {status_cod}; uuid = {uuid}; status_time = {status_time}; caller = {caller}")
        await user_service.set_status_by_aster(
            uuid=uuid, 
            status_code=status_cod, 
            status_time=status_time, 
            incoming_call=caller, 
            call_id=call_id, 
            script_ivr_hyperscript=script_ivr_hyperscript
            )
        if status_cod.upper() in Events:
            res = await Events[status_cod.upper()](id=call_id, phone=caller)
            log.debug(f"status: {status_cod}, code: {res}")
        result = {
            "message": "set status"
        }
    except Exception as e:
        err = default_error(e, source='UserService')
        response.status_code = err[0]
        result = {
            "message": err[1]
        }
    return result

@route.websocket("/ws", "user_status")
@inject
async def ws_channel_user_status(
    websocket: WebSocket,
    user_service: UserService = Depends(Provide[Container.user_service])
):
    await websocket.accept()
    queue = asyncio.queues.Queue()
    try:
        async def read_from_socket(websocket: WebSocket):
            async for data in websocket.iter_json():
                queue.put_nowait(data)
        async def get_data_and_send():
            data = await queue.get()
            fetch_task = asyncio.create_task(user_service.redis_pub_sub(websocket, data['user_id']))
            while True:
                data = await queue.get()
                if not fetch_task.done():
                    fetch_task.cancel()
                fetch_task = asyncio.create_task(user_service.redis_pub_sub(websocket, data['user_id']))
        await asyncio.gather(read_from_socket(websocket), get_data_and_send())
    except Exception as e:
        log.error(e, stack_info=True)
        websocket.close()

@route.get("/fill",  include_in_schema=False)
@inject
async def fill(
    user_service: UserService = Depends(Provide[Container.user_service])
):
    await user_service.add_status_to_redis()
    await user_service.all()
    await user_service.add_status_user_to_redis()

@route.get('/end_call')
@inject
async def update_status(
    call_id: str,
    user_service: UserService = Depends(Provide[Container.user_service])):
    params = user_service.get_call_by_call_id(call_id)
    await send_call_patch(call_id, params['disposition'], params['billsec'], params['files'])
    await user_service.push_filename_asterisk(params['files'], params['calldate'])
    