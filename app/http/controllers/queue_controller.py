from fastapi import Depends, APIRouter, Response, status, Body, Request, HTTPException
from datetime import datetime
from dependency_injector.wiring import inject, Provide
from app.kernel.container import Container

route = APIRouter(
    prefix="/queue",
    tags=['queue'],
    responses={404: {"description": "Not found"}} 
)

