import jwt
import os
import re
from dependency_injector.wiring import inject, Provide
from fastapi import status, responses, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from app.kernel.container import Container
from app.http.services.access import Access
from app.http.services.jwt_managment import JwtManagement, TokenInBlackList
from app.database.repository.super import UserIsFired

# Проверка осущетвляется перед проверки авторизации
path_exception = ("docs", "openapi.json", "images", "audio")
# Проверка осущетвляется перед проверки авторизации
path_exception_global = (
        "/users/status/asterisk", 
        "/users/status/test", 
        "/users/status/fill",
        "/users/status/end_call", 
        "/users/fill", 
        "/auth/login",
        "/auth/logout"
    )
# Проверка осущетвляется после проверки авторизации
user_path_exception_map = {
    "get": (
        "/users/status", 
        "/users/current", 
        "/users/departments", 
        "/queue", 
        "/users/inner_phone/settings",
        "/users/inner_phone/user",
        "/users/analytics",
        "/users/departments",
        "/users/(\d{1,})"
    ),
    "patch": (
        "/users/status"
    )
}

@inject
def get_user(id, user_repository = Depends(Provide[Container.user_repository])):
    return user_repository.get_by_id(id)

@inject
def get_user_permission(user, user_repository = Depends(Provide[Container.user_repository])):
    user_roles:dict = user_repository.get_user_permission(user.id)
    roles = user_repository.get_role_permission(user.id)
    if user_roles != {}:
        roles = user_roles
    return roles

@inject
async def redis(jwt_m: JwtManagement = Depends(Provide[Container.jwt])):
    return await jwt_m.generate()

class Auth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            path = str(request.get("path")).split("/")
            if  path[1] in path_exception:
                return await call_next(request)
            if request.get("path") in path_exception_global:
                return await call_next(request)
            token = request.headers.get('authorization')
            if token is None:
                return responses.JSONResponse(
                    content={
                        "messgae": "No auth",
                        "description": "Нет авторизации"
                        },
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            token = token.replace("Bearer ", "")
            generate = await redis()
            async with generate as g:
                await g.check_black_list(token)
            decode_jwt = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            request.state.current_user_id = decode_jwt['azp']
            request.state.token = token
            if decode_jwt['azp'] == 0:
                return await call_next(request)
            user = get_user(decode_jwt['azp'])
            if user.employment_status == False or user.date_dismissal_at is not None:
                raise UserIsFired()
            method = request.method.lower()
            if method in user_path_exception_map:
                exceptions_paths = user_path_exception_map[method]
                for upx in exceptions_paths:
                    if re.search(upx, request.get("path")) is not None:
                        return await call_next(request)
            access = Access(method=method)
            perms = get_user_permission(user).items()
            for _, value in perms:
                if path[1] in value['permissions']:
                    map_access = value['permissions'][path[1]]
                    access.set_access_model(map_access['method_access'])
                    request.state.for_user = {
                        "status": access.check_personal(),
                        "user": user
                    }
                    if access.check_access_method():
                        return await call_next(request)
            return responses.JSONResponse(
                content={
                    "message": "the module is not available, for this role",
                    "description": "Запрещено для роли этого пользователя."
                },
                status_code=status.HTTP_423_LOCKED
            )
        except UserIsFired:
            return responses.JSONResponse(
                content={
                    "message": "The user is fired",  # "Token Signature expired"
                    "description": "Пользователь уволен"
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except jwt.exceptions.ExpiredSignatureError as signature:
            return responses.JSONResponse(
                content={
                    "message": str(signature),  # "Token Signature expired"
                    "description": "Срок действия токена истек. Войдите в систему еще раз."
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except TokenInBlackList as token:
            return responses.JSONResponse(
                content={
                    "message": str(token),  # "Token blacklisted. Login again."
                    "description": "Токен заблокирован. Войдите в систему еще раз."
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except jwt.DecodeError as decode:
            return responses.JSONResponse(
                content={
                    "message": str(decode),  # "Invaid JWT generated."
                    "description": "Сгенерирован недопустимый JWT."
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
