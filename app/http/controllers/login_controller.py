import os, jwt, typing
from hashlib import sha256
from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.security import HTTPBearer
from dependency_injector.wiring import Provide, inject
from app.http.services.helpers import default_error
from app.http.services.users import UserLoginParams, UserService
from app.http.services.jwt_managment import JwtManagement, TokenNotFound
from app.database import NotFoundError, UnauthorizedException
from app.kernel import Container
from app.http.services.jwt_managment import TokenInBlackList

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
    """
    Exceptions:
        DecodeError
    """
    try:
        result = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
    except jwt.DecodeError:
        raise
    return result

@route.get("/logout")
@inject
async def logout(
    request: Request,
    response: Response,
    user_service: UserService = Depends(Provide[Container.user_service]),
    jwt_m: JwtManagement = Depends(Provide[Container.jwt]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """
    Exceptions:
        InvalidSignatureError
        NotFoundError
        TokenInBlackList
        TokenNotFound
        DecodeError
    """
    try:
        access_token = get_token(request)
        decode = token_decode(access_token)
        user = user_service.by_id(decode['azp'])
        jwt_gen = await jwt_m.generate(user)
        await user_service.set_status(decode['azp'], 15)
        async with jwt_gen as j:
            if decode['type'] == "a" and 'rf' in decode:
                await j.add_to_black_list(decode['rf'])
            await j.check_black_list(access_token)
            await j.add_to_black_list(access_token)    
            # await j.add_to_black_list(tokens['access_token'])
            # await j.add_to_black_list(tokens['refresh_token'])
            result = {
                "message": "logout success",
                "description": "Успешный выход из системы"
            }
    except jwt.exceptions.ExpiredSignatureError as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": str(e),  # "Token Signature expired"
            "description": "Срок действия токена истек. Войдите в систему еще раз."
        }
    except TokenInBlackList as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": str(e),  # "Token blacklisted. Login again."
            "description": "Токен заблокирован. Войдите в систему еще раз."
        }
    except jwt.DecodeError as e:
        response.status_code=status.HTTP_401_UNAUTHORIZED
        return {
            "message": str(e),  # "Invaid JWT generated."
            "description": "Сгенерирован недопустимый JWT."
        }
    except UnauthorizedException as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": str(e),  # "Token blacklisted. Login again."
            "description": "Вы не авторизованы"
        }
    except Exception as e:
        err = default_error(e, source='UserAuth')
        response.status_code = err[0]
        result = err[1]
    return result


@route.get("/refresh")
@inject
async def refresh(
    request: Request,
    response: Response,
    user_service: UserService = Depends(Provide[Container.user_service]),
    jwt_m: JwtManagement = Depends(Provide[Container.jwt]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """_summary_

    Exceptions:
        InvalidSignatureError
        NotFoundError
        TokenInBlackList
        TokenNotFound
        ExpiredSignatureError
    """
    try:
        access_token = get_token(request)
        decode = token_decode(access_token)
        user = user_service.by_id(decode['azp'])
        jwt_gen = await jwt_m.generate(user)
        async with jwt_gen as j:
            await j.get_tokens()
            await j.add_to_black_list(access_token)
            tokens = await j.tokens()
            result = tokens
    except jwt.exceptions.ExpiredSignatureError as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": str(e),  # "Token Signature expired"
            "description": "Срок действия токена истек. Войдите в систему еще раз."
        }
    except TokenInBlackList as e:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": str(e),  # "Token blacklisted. Login again."
            "description": "Токен заблокирован. Войдите в систему еще раз."
        }
    except jwt.DecodeError as e:
        response.status_code=status.HTTP_401_UNAUTHORIZED
        return {
            "message": str(e),  # "Invaid JWT generated."
            "description": "Сгенерирован недопустимый JWT."
        }
    except Exception as e:
        err = default_error(e, source='UserAuth')
        response.status_code = err[0]
        result = err[1]
    return result

@route.post("/login")
@inject
async def login(
    params: UserLoginParams,
    response: Response,
    user_service: UserService = Depends(Provide[Container.user_service]),
    jwt: JwtManagement = Depends(Provide[Container.jwt])):
    """
    Exceptions:
        NotFoundError
    """
    password = sha256(params.password.encode()).hexdigest()
    try:
        user = user_service.find_user_by_login(params.login)
        await user_service.set_status(user.id, 18)
        await user_service.set_status(user.id, 15)
    except NotFoundError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": "Invalid login",
            "description": "Логин неверный"
        }
    if user.hashed_password is None:
        user.hashed_password = sha256(user.password.encode()).hexdigest()
    if password != user.hashed_password:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            "message": "The password is incorrect",
            "description": "Пароль неверный"
        }
    jwt_manager = await jwt.generate(user)
    async with jwt_manager as j:
        tokens = await j.tokens()
        return tokens
