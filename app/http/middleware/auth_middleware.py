from starlette.middleware.base import BaseHTTPMiddleware

class Auth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        next = await call_next(request)
        if "/auth/login" == request.get("path"):
            return next
        print(request.cookies)
        return next