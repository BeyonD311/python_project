from fastapi import Depends, APIRouter, Response
from fastapi.security import HTTPBearer
from app.http.services.queue import QueueStatisticsService, PeriodsLoadQueue, PeriodsActiveQueue
from dependency_injector.wiring import Provide, inject
from app.kernel.container import Container
from app.http.services.helpers import default_error
from pydantic import ValidationError

route = APIRouter(
    prefix="/queue/statistics",
    tags=['queues_statistics'],
    responses={404: {"description": "Not found"}} 
)

security = HTTPBearer()


@route.get("/loading/{uuid}")
@inject
def loading_the_queue(
    uuid: str, 
    period: PeriodsLoadQueue,
    response: Response,
    stat_service: QueueStatisticsService = Depends(Provide[Container.queue_statistics_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        result = stat_service.queue_load(uuid, type_period=period)
    except Exception as e:
        err = default_error(e)
        response.status_code = err[0]
        result = err[1]
    return result

@route.get("/active_queues")
@inject
def operation_of_active_queues(
    period: PeriodsActiveQueue,
    response: Response,
    stat_service: QueueStatisticsService = Depends(Provide[Container.queue_statistics_service]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        result = stat_service.active_queues(period)
    except Exception as e:
        err = default_error(e)
        response.status_code = err[0]
        result = err[1]
    return result