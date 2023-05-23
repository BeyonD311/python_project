from datetime import date
from fastapi import APIRouter, Depends, status, Response
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.database import NotFoundError
from app.http.services.users import UserService
from app.kernel import Container
from app.http.services.analytics.analytics import AnalyticsService
from app.http.services.analytics.analytics_base_model import DisposalAnalytic, AntAnalytic, CallAnalytic, \
    CalculationMethod

security = HTTPBearer()

route = APIRouter(
    prefix="/users/analytics",
    tags=['analytics'],
    responses={404: {"description": "Not found"}}
)


@route.get('/disposal')
@inject
async def get_disposal_analytic(
        user_id: int,
        beginning: date,
        ending: date,
        response: Response,
        calculation_method: CalculationMethod = CalculationMethod.SUM,
        analytics_service: AnalyticsService = Depends(Provide[Container.analytics_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        disposal_data = DisposalAnalytic(user_id=user_id, beginning=beginning, ending=ending,
                                         calculation_method=calculation_method)
        result = analytics_service.get_disposal_analytic(data=disposal_data)
        return result
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }
    except NotFoundError as e:
        return {
            'message': str(e)
        }


@route.get('/ant')
@inject
async def get_ant_analytic(
        user_id: int,
        beginning: date,
        ending: date,
        response: Response,
        calculation_method: CalculationMethod = CalculationMethod.SUM,
        analytics_service: AnalyticsService = Depends(Provide[Container.analytics_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        ant_data = AntAnalytic(user_id=user_id, beginning=beginning, ending=ending,
                               calculation_method=calculation_method)
        result = analytics_service.get_ant_analytic(data=ant_data)
        return result
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }
    except NotFoundError as e:
        return {
            'message': str(e)
        }


@route.get('/call')
@inject
async def get_call_analytic(
        beginning: date,
        ending: date,
        number: str,
        response: Response,
        analytics_service: AnalyticsService = Depends(Provide[Container.analytics_service]),
        HTTPBearerSecurity: HTTPBearer = Depends(security)
):
    try:
        call_data = CallAnalytic(beginning=beginning, ending=ending, number=number)
        result = analytics_service.get_call_analytic(data=call_data)
        return result
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            'message': str(e)
        }
