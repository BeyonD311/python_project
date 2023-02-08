import os
import jwt
from hashlib import sha256
from fastapi import APIRouter, Depends, status, Response, Request
from dependency_injector.wiring import Provide, inject
from app.http.services import UserLoginParams, UserService, JwtManagement, RolesPermission
from app.database import NotFoundError
from app.kernel import Container

route = APIRouter(
    prefix="/auth",
    tags=['auth'],
)

@route.get("/refresh")
@inject
async def login(
    request: Request,
    response: Response,
    user_servive: UserService = Depends(Provide[Container.user_service]),
    jwt_m: JwtManagement = Depends(Provide[Container.jwt])):
    try:
        access_token = request.headers.get('authorization').replace("Bearer ", "")
        decode = jwt.decode(access_token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        user = user_servive.get_user_by_id(decode['azp'])
        
    except jwt.exceptions.InvalidSignatureError as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "message": str(e)
        }
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            "massage": "user not found"
        }
    
@route.post("/login")
@inject
async def login(
    params: UserLoginParams,
    response: Response,
    user_servive: UserService = Depends(Provide[Container.user_service]),
    jwt: JwtManagement = Depends(Provide[Container.jwt])):
    password = sha256(params.password.encode()).hexdigest()
    try:
        user = user_servive.find_user_by_login(params.login)
    except NotFoundError as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": "Логин не верный" 
        }
    
    if password != user.hashed_password:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": "Пароль не верный" 
        }
    jwt_manager = await jwt.generate(user)
    async with jwt_manager as j:
        tokens = await j.tokens()
        return tokens
    
