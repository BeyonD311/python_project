import jwt
import os
from dependency_injector.wiring import inject, Provide
from fastapi import status, responses, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from app.kernel.container import Container
from app.http.services.helpers import parse_access

@inject
def get_user(id, user = Depends(Provide[Container.user_service])):
    return user.get_user_by_id(id, True)

class Auth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = str(request.get("path")).split("/")
        if "auth" == path[1] or "docs" == path[1] or "openapi.json" == path[1]:
            return await call_next(request)
        token = request.headers.get('authorization')
        if token is None:
            return responses.JSONResponse(content= {
                "messgae": "No auth"
            },status_code=status.HTTP_401_UNAUTHORIZED)
        token = token.replace("Bearer ", "")
        try:
            decode_jwt = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            if decode_jwt['azp'] == 0:
                return await call_next(request)
            user = get_user(decode_jwt['azp'])
            method = request.method.lower()
            roles = {r.id:r for r in user.roles}
            if 1 in roles:
                return await call_next(request)
            for role in roles:
                role = roles[role]
                modules = {m.module_id: parse_access(m.method_access) for m in role.permission_model}
                permissions = {p.module_name: modules[p.id] for p in role.permissions}
                if path[1] in permissions:
                    map_access = permissions[path[1]].map
                    print("------------------")
                    print(map_access[method])
                    print("------------------")
                    if method in map_access and map_access[method]:
                        return await call_next(request)
            return responses.JSONResponse(content= {
                "messgae": "the module is not available, for this role"
            },status_code=status.HTTP_423_LOCKED)
        except jwt.exceptions.ExpiredSignatureError as e:
            return responses.JSONResponse(content= {
                "messgae": str(e)
            },status_code=status.HTTP_401_UNAUTHORIZED)
        
    