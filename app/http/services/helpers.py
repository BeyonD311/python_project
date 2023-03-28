import re
from aioredis import Redis
from fastapi import status
from pydantic import BaseModel

__all__ = ["default_error", "message"]

class RedisInstance():
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
    def __enter__(self):
        return self.redis
    def __exit__(self, exc_type, exc_value, exc_traceback):
        print(exc_type, exc_value, exc_traceback)
        del self 

def default_error(error: Exception):
    from app.http.services import TokenInBlackList, TokenNotFound
    from app.database import NotFoundError
    from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError

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
    
    raise error

def message(message):
    return {
        "message": str(message)
    }

def parse_params_num(params: str) -> set:
    reg = re.findall(r'[0-9]{1,}', params)
    result = {*reg}
    return result