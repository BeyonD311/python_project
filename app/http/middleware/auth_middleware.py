from starlette.middleware.base import BaseHTTPMiddleware

class Auth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        print(request.get("path"))
        next = await call_next(request)
        if "/auth/login" == request.get("path"):
            return next
        return next