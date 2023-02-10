import os
import jwt
import typing
from hashlib import sha256
from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.http.services import UserLoginParams, UserService, JwtManagement, RolesPermission, TokenInBlackList, TokenNotFound
from app.database import NotFoundError
from app.kernel import Container

route = APIRouter(
    prefix="/auth",
    tags=['auth'],
)

security = HTTPBearer()

def get_token(request: Request) -> str:
    access_token = request.headers.get('authorization')
    if access_token is None:
        raise TokenNotFound
    return access_token.replace("Bearer", "").strip()

def token_decode(token: str) -> typing.Mapping:
    return jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])

@route.get("/logout")
@inject
async def logout(
    request: Request,
    response: Response,
    user_servive: UserService = Depends(Provide[Container.user_service]),
    jwt_m: JwtManagement = Depends(Provide[Container.jwt]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    
    try:
        access_token = get_token(request)
        decode = token_decode(access_token)
        user = user_servive.get_user_by_id(decode['azp'], True)
        jwt_gen = await jwt_m.generate(user)
        async with jwt_gen as j:
            tokens = await j.get_tokens() 
            await j.add_to_black_list(tokens['access_token'])
            await j.add_to_black_list(tokens['refresh_token'])
            await j.remove_token()
            return {
                "message": "logout success"
            }
            
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
    except TokenInBlackList as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "massage": str(e)
        }
    except TokenNotFound as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "massage": "Pleace auth"
        }
    except jwt.exceptions.ExpiredSignatureError as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "massage": "Signature has expired"
        }

@route.get("/refresh")
@inject
async def refresh(
    request: Request,
    response: Response,
    user_servive: UserService = Depends(Provide[Container.user_service]),
    jwt_m: JwtManagement = Depends(Provide[Container.jwt]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        access_token = get_token(request)
        decode = token_decode(access_token)
        user = user_servive.get_user_by_id(decode['azp'], True)
        jwt_gen = await jwt_m.generate(user)
        async with jwt_gen as j:
            await j.get_tokens()
            await j.add_to_black_list(access_token)
            tokens = await j.tokens()
            return tokens
            
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
    except TokenInBlackList as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "massage": str(e)
        }
    except TokenNotFound as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "massage": "Pleace auth"
        }
    except jwt.exceptions.ExpiredSignatureError as e:
        response.status_code = status.HTTP_409_CONFLICT
        return {
            "massage": "Signature has expired"
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
    
