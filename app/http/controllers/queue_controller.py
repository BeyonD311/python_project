import asyncio
from fastapi import Depends, APIRouter, Response
from fastapi.security import HTTPBearer
from app.http.services.queue import QueueService
from app.http.services.queue import RequestQueue
from app.http.services.queue import RequestQueueMembers
from app.http.services.queue import GetAllQueue
from app.http.services.queue import Filter
from app.http.services.queue import AddPhonesToTheQueue
from dependency_injector.wiring import inject
from dependency_injector.wiring import Provide
from app.kernel.container import Container
from app.http.services.helpers import default_error

route = APIRouter(
    prefix="/queue",
    tags=['queue'],
    responses={404: {"description": "Not found"}} 
)

security = HTTPBearer()

@route.get("")
@inject
async def get_queue(
    response: Response,
    page: int = 1,
    size: int = 10,
    order_field: str  = "name",
    order_direction:str = "desc",
    filter:str = "", 
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    """ 
    описание полей \n
        ** order_field - поле сортировки (name, status, type, operators)
        ** order_direction - направление сортировки(asc,desc)
        ** filter - должен содержать строку типа \n
                    name=Название очереди;
                    status=1,2;
                    type=Название;
                    user_id=(int) для фильтрации очередей по user_id
    """
    try:
        split_filter = filter.split(";")
        params = GetAllQueue(
            page=page,
            size=size,
            order_field=order_field,
            order_direction=order_direction
        )
        split_params = []
        for filter in split_filter:
            filter = filter.split("=")
            if len(filter) > 1:
                split_params.append(filter)
        if len(split_params) > 0:
            for params_filter in split_params:
                params.filter.append(Filter(
                    field=params_filter[0].upper(),
                    value=params_filter[1]
                ))
        result = queue_service.get_queues(params)
    except Exception as exception:
        err = default_error(exception, source='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/params")
@inject
async def get_queue_params(
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    params = await queue_service.get_default_params()
    return params

@route.get("/resources/queues")
@inject
async def get_resources_queues_by_user_id(
    id: int, 
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    queue_name: str = "",
):
    """ 
        Получение очередей для оператора по id пользователя \n
        **name_queue - для фильтрации по имени очереди
    """
    return queue_service.get_queues_is_selected(id, queue_name)

@route.post("/resources/queues")
@inject
async def add_phones_to_the_queue(
    params: AddPhonesToTheQueue,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security),
):
    """ 
        Добавить внутренние номера к очереди
    """
    result = {}
    try:
        result = queue_service.add_phones_to_the_queue(params)
    except Exception as exception:
        err = default_error(exception, source='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/resources")
@inject
async def get_queue_members(
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    uuid: str = None, 
    operators: str = "",
    supervisor: str = ""
):
    """ 
        Получение доступных ресурсов
        ** operators - фильтр по ФИО
        ** supervisor - фильтр по ФИО
    """
    return queue_service.get_queue_members(uuid, operators, supervisor)

@route.get("/{uuid}")
@inject
async def get_queue_by_uuid(
    uuid: str,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    result = {}
    try:
        return await queue_service.get_queue_by_uuid(uuid)
    except Exception as exception:
        err = default_error(exception, source='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/card/{uuid}")
@inject
async def get_queue_by_uuid_card(
    uuid: str,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    """ С заменой параметров """
    result = {}
    try:
        return await queue_service.get_queue_by_uuid_for_card(uuid)
    except Exception as exception:
        err = default_error(exception, source='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/state/{uuid}")
@inject
async def get_queue_state(
    uuid: str,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    result = {}
    try:
        result = queue_service.get_state_queue(uuid)
    except Exception as exception:
        err = default_error(exception, source='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/statuses/{uuids}")
@inject
async def get_queue_statuses(
    uuids: str,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    """
      Статусы для очереди\n
        uuid через запятую
     """
    result = {}
    try:
        uuids = uuids.split(",")
        result = queue_service.get_status(uuids)
    except Exception as exception:
        err = default_error(exception, item='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.post("/resources/{uuid}")
@inject
async def save_queue_members(
    uuid: str,
    params: RequestQueueMembers,
    response: Response, 
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    result = {}
    try:
        result = queue_service.save_queue_members(uuid, params)
    except Exception as exception:
        err = default_error(exception, item='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.post("")
@inject
async def add_create_queue(
    params: RequestQueue,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    """ Создание очереди в asterisk """
    result = {}
    try:
        result = queue_service.add(params=params)
    except Exception as exception:
        err = default_error(exception, source='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.put("/{uuid}")
@inject
async def add_update_queue(
    uuid: str,
    params: RequestQueue,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    """ Создание очереди в asterisk """
    result = {}
    try:
        result = queue_service.update(uuid=uuid,params=params)
    except Exception as exception:
        err = default_error(exception, source='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.patch("/set_state/{uuid}")
@inject
async def add_set_state_queue(
    uuid: str,
    state: bool,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    result = {}
    try:
        result = queue_service.set_state(uuid, state)
    except Exception as exception:
        err = default_error(exception, source='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.delete("/{uuid}")
@inject
async def delete_queue(
    uuid: str,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    result = {}
    try:
        result = queue_service.delete(uuid)
    except Exception as exception:
        err = default_error(exception, item='Queue')
        response.status_code = err[0]
        result = err[1]
    return result