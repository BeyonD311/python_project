from enum import Enum

from fastapi import APIRouter, Depends, status, Response
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.http.services.helpers import parse_params_num
from app.database import NotFoundError
from app.kernel import Container
from app.http.services.analytics.analytics import AnalyticsService
from app.http.services.analytics.analytics_base_model import DisposalAnalytic, AntAnalytic, CallAnalytic

security = HTTPBearer()

route = APIRouter(
    prefix="/users/analytics",
    tags=['analytics'],
    responses={404: {"description": "Not found"}}
)


@route.post('/disposal')
@inject
async def get_disposal_analytic(
        data: DisposalAnalytic,
        response: Response,
        analytics_service: AnalyticsService = Depends(Provide[Container.analytics_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        result = analytics_service.get_disposal_analytic(data=data)
        return result
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }


@route.post('/ant')
@inject
async def get_ant_analytic(
        data: AntAnalytic,
        response: Response,
        analytics_service: AnalyticsService = Depends(Provide[Container.analytics_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        result = analytics_service.get_ant_analytic(data=data)
        return result
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }


@route.post('/call')
@inject
async def get_call_analytic(
        data: CallAnalytic,
        response: Response,
        analytics_service: AnalyticsService = Depends(Provide[Container.analytics_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        result = analytics_service.get_call_analytic(data=data)
        return result
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }