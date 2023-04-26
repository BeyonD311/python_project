from fastapi import Depends, APIRouter, Response
from fastapi.security import HTTPBearer
from app.http.services.queue import QueueService
from app.http.services.queue import RequestQueue
from dependency_injector.wiring import inject
from dependency_injector.wiring import Provide
from app.kernel.container import Container

route = APIRouter(
    prefix="/queue",
    tags=['queue'],
    responses={404: {"description": "Not found"}} 
)

security = HTTPBearer()

@route.get("/{name}")
@inject
async def get_queue_by_name(
    name: str,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    return queue_service.get_queue_by_name(name)

@route.post("")
@inject
async def add_create_queue(
    params: RequestQueue,
    response: Response,
    queue_service: QueueService = Depends(Provide[Container.queue_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    queue_service.add(params=params)

