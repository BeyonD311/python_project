import jwt
import os
from dependency_injector.wiring import inject, Provide
from fastapi import status, responses, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from app.kernel.container import Container
from app.http.services.access import Access
from app.http.services.jwt_managment import JwtManagement, TokenInBlackList

path_exception = ("auth", "docs", "openapi.json", "images")
path_exception_aster = ("/users/status/asterisk", "/users/status/test", "/users/status/fill", "/users/fill")

user_path_exception = ("/users/status", "/users/current", "users/departments", "/queue")

@inject
def get_user(id, user_repository = Depends(Provide[Container.user_repository])):
    return user_repository.get_by_id(id)

@inject
def get_user_permission(user, user_repository = Depends(Provide[Container.user_repository])):
    user_roles:dict = user_repository.get_user_permission(user.id)
    roles = user_repository.get_role_permission(user.id)
    for key, user_role in user_roles.items():
        if key in roles:
            roles[key] = user_role
    return roles

@inject
async def redis(jwt_m: JwtManagement = Depends(Provide[Container.jwt])):
    return await jwt_m.generate()

class Auth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = str(request.get("path")).split("/")
        if  path[1] in path_exception:
            return await call_next(request)
        if request.get("path") in path_exception_aster:
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
        try:
            generate = await redis()
            async with generate as g:
                await g.check_black_list(token)
            decode_jwt = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            request.state.current_user_id = decode_jwt['azp']
            request.state.token = token
            if decode_jwt['azp'] == 0:
                return await call_next(request)
            user = get_user(decode_jwt['azp'])
            method = request.method.lower()
            if str(request.get("path")) in user_path_exception:
                return await call_next(request)
            access = Access(method=method)
            perms = get_user_permission(user).items()
            print(perms)
            for role_id, value in perms:
                
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
        except jwt.exceptions.ExpiredSignatureError as e:
            return responses.JSONResponse(
                content={
                    "message": str(e),  # "Token Signature expired"
                    "description": "Срок действия токена истек. Войдите в систему еще раз."
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except TokenInBlackList as e:
            return responses.JSONResponse(
                content={
                    "message": str(e),  # "Token blacklisted. Login again."
                    "description": "Токен заблокирован. Войдите в систему еще раз."
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except jwt.DecodeError as e:
            return responses.JSONResponse(
                content={
                    "message": str(e),  # "Invaid JWT generated."
                    "description": "Сгенерирован недопустимый JWT."
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
