from fastapi import APIRouter, Depends, status, Response
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.http.services.helpers import parse_params_num
from app.database import NotFoundError
from app.kernel import Container

security = HTTPBearer()

route = APIRouter(
    prefix="/users/analytics",
    tags=['status'],
    responses={404: {"description": "Not found"}} 
)
