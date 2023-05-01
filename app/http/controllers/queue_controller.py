from fastapi import Depends, APIRouter, Response
from fastapi.security import HTTPBearer
from app.http.services.queue import QueueService
from app.http.services.queue import RequestQueue
from app.http.services.queue import RequestQueueMembers
from app.http.services.queue import GetAllQueue
from app.http.services.queue import Filter
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
    split_filter = filter.split(";")
    params = GetAllQueue(
        page=page,
        size=size,
        order_field=order_field,
        order_direction=order_direction
    )
    for filter in split_filter:
        split_params = filter.split("=")
        if len(split_params) > 1:
            params.filter.append(Filter(
                field=split_params[0].upper(),
                value=split_params[1]
            ))

    return queue_service.get_queues(params)
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
        return queue_service.get_queue_by_uuid(uuid)
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
        err = default_error(exception, item='Queue')
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
        err = default_error(exception, item='Queue')
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/resources/{uuid}")
@inject
async def get_queue_members(
    uuid: str,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security),
    operators: str = "",
    supervisor: str = ""
):
    return queue_service.get_queue_members(uuid, operators, supervisor)

@route.post("/resources/{uuid}")
@inject
async def save_queue_members(
    uuid: str,
    params: RequestQueueMembers,
    response: Response, 
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    return queue_service.save_queue_members(uuid, params)
