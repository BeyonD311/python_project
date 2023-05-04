from fastapi import APIRouter, Depends, Response, status
from dependency_injector.wiring import inject, Provide

from app.database import NotFoundError
from app.kernel.container import Container
from app.http.services.schedule.schedule import ScheduleService
from app.http.services.schedule.schedule_base_model import ScheduleCreate, ScheduleUpdate, ScheduleRead, Pagination, \
    Order
from fastapi.security import HTTPBearer
from sqlalchemy.exc import IntegrityError

security = HTTPBearer()

route = APIRouter(
    prefix='/schedules',
    tags=['schedules'],
    responses={404: {'description': 'Not found'}}
)


@route.get('/')
@inject
async def get_all(
        queue_name: str,
        order_field: str = 'beginning',
        order_direction: str = 'asc',
        page: int = 1,
        size: int = 10,
        schedule_service: ScheduleService = Depends(Provide[Container.schedule_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    return schedule_service.get_all_by_queue_name(queue_name=queue_name,
                                                  pagination=Pagination(page=page, size=size),
                                                  order=Order(field=order_field, direction=order_direction))


@route.get('/{schedule_id}')
@inject
async def get_by_id(
        schedule_id: int,
        response: Response,
        schedule_service: ScheduleService = Depends(Provide[Container.schedule_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
) -> ScheduleRead:
    try:
        return schedule_service.get_by_id(schedule_id=schedule_id)
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }


@route.post('/')
@inject
async def create(
        schedule: ScheduleCreate,
        response: Response,
        schedule_service: ScheduleService = Depends(Provide[Container.schedule_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
) -> ScheduleRead:
    try:
        return schedule_service.create(schedule=schedule)
    except IntegrityError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e.orig)
        }
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }


@route.delete('/{schedule_id}')
@inject
async def delete(
        schedule_id: int,
        response: Response,
        schedule_service: ScheduleService = Depends(Provide[Container.schedule_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        schedule_service.delete(schedule_id=schedule_id)
        response.status_code = status.HTTP_200_OK
        return {
            'message': "Deleted successfully"
        }
    except NotFoundError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }


@route.put('/{schedule_id}')
@inject
async def update(
        schedule_id: int,
        update_data: ScheduleUpdate,
        response: Response,
        schedule_service: ScheduleService = Depends(Provide[Container.schedule_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        schedule_service.update(schedule_id=schedule_id, update_data=update_data)
        response.status_code = status.HTTP_200_OK
        return {
            'message': "Updated successfully"
        }
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'message': str(e)
        }


@route.patch('/{schedule_id}')
@inject
async def update_status(
        schedule_id: int,
        schedule_status: bool,
        response: Response,
        schedule_service: ScheduleService = Depends(Provide[Container.schedule_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        schedule_service.update_status(schedule_id=schedule_id, status=schedule_status)
        response.status_code = status.HTTP_200_OK
        return {
            'message': "Updated successfully"
        }
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'message': str(e)
        }
