from fastapi import APIRouter
from app.http.services import UserLoginParams

route = APIRouter(
    prefix="/auth",
    tags=['auth'],
)

@route.get("/login")
async def login():
    return "login"
