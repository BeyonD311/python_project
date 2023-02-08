from fastapi import status, responses
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class Auth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = str(request.get("path"))
        if "/auth/login" == path:
            return await call_next(request)
        token = request.headers.get('authorization')
        response = await call_next(request)
        if token is None:
            response = await RequestResponseEndpoint()

            return call_next(response)
        