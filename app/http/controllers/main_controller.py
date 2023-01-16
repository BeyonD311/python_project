from fastapi import Depends, APIRouter, HTTPException, Response, status
from dependency_injector.wiring import inject, Provide
# import app.database

route = APIRouter(tags=['main_page'])

@route.get("/")
async def main_page():
    return "This main page"