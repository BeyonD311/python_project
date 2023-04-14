import re
from aioredis import Redis
from fastapi import status
from fastapi.websockets import WebSocket
from asyncio.queues import Queue

__all__ = ["default_error", "message", "read_from_socket"]

class RedisInstance():
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
    def __enter__(self):
        return self.redis
    def __exit__(self, exc_type, exc_value, exc_traceback):
        del self 

def default_error(error: Exception):
    from app.http.services.jwt_managment import TokenInBlackList, TokenNotFound
    from app.database import NotFoundError
    from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError
    from sqlalchemy.exc import IntegrityError

    if isinstance(error, InvalidSignatureError):
        return status.HTTP_409_CONFLICT, message(error)
    if isinstance(error, NotFoundError):
        return status.HTTP_404_NOT_FOUND, message("user not found")
    if isinstance(error, TokenInBlackList):
        return status.HTTP_400_BAD_REQUEST, message(error)
    if isinstance(error, TokenNotFound):
        return status.HTTP_401_UNAUTHORIZED, message("Pleace auth")
    if isinstance(error, ExpiredSignatureError):
        return status.HTTP_409_CONFLICT, message("Signature has expired")
    if isinstance(error, IntegrityError):
        info_error = str(error.orig.__repr__())
        detail = re.findall(r"(?:DETAIL:(.*\(.*\))(.*)?(\".*\"))", info_error)
        if detail is not None:
            detail = str(error)
        else:
            detail = "error"
        return status.HTTP_409_CONFLICT, message(detail)
    raise error

def message(message):
    return {
        "message": str(message)
    }

def parse_params_num(params: str) -> set:
    reg = re.findall(r'[0-9]{1,}', params)
    result = {*reg}
    return result

async def read_from_socket(websocket: WebSocket, queue: Queue):
    async for data in websocket.iter_json():
        print(data)
        queue.put_nowait(data)