import re
from datetime import time
from aioredis import Redis
from fastapi import status
from fastapi.websockets import WebSocket
from asyncio.queues import Queue

__all__ = ["default_error", "message", "read_from_socket", "convert_second_to_time", "convert_time_to_second"]

class RedisInstance():
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
    def __enter__(self):
        return self.redis
    def __exit__(self, exc_type, exc_value, exc_traceback):
        del self 

def default_error(error: Exception, item=None):
    from app.http.services.jwt_managment import TokenInBlackList, TokenNotFound
    from app.database import (
        NotFoundError, ExpectationError, ExistsException, AccessException,
        RequestException, BadFileException
    )
    from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError
    from jwt import DecodeError
    from sqlalchemy.exc import (
        IntegrityError, DataError
    )
    from websockets.exceptions import ConnectionClosedError
    from json.decoder import JSONDecodeError

    if hasattr(error, "entity_description"):
        err_description = error.entity_description
    if isinstance(error, RequestException):
        return status.HTTP_400_BAD_REQUEST, message(message=error)
    if isinstance(error, TokenInBlackList):
        return status.HTTP_400_BAD_REQUEST, message(message=error, description=err_description)
    if isinstance(error, BadFileException):
        return status.HTTP_400_BAD_REQUEST, message(message=error, description=err_description)
    if isinstance(error, ExistsException):
        return status.HTTP_400_BAD_REQUEST, message(message=f"Already exists {item}.", description=err_description)
    if isinstance(error, TokenNotFound):
        return status.HTTP_401_UNAUTHORIZED, message(message="Pleace auth")
    if isinstance(error, DecodeError):
        return status.HTTP_401_UNAUTHORIZED, message(message="Invaid JWT generated.")
    if isinstance (error, AccessException):
        return status.HTTP_403_FORBIDDEN, message(message="Resource not available")
    if isinstance(error, NotFoundError):
        return status.HTTP_404_NOT_FOUND, message(message=f"Not found {item}.", description=err_description)
    if isinstance(error, InvalidSignatureError):
        return status.HTTP_409_CONFLICT, message(message=error)
    if isinstance(error, ExpiredSignatureError):
        return status.HTTP_409_CONFLICT, message(message="Signature has expired")
    if isinstance(error, ExpectationError):
        # TODO: meybe better "422 Unprocessable Entity («необрабатываемый экземпляр»)"
        return status.HTTP_417_EXPECTATION_FAILED, message(message="", description=err_description)
    if isinstance(error, IntegrityError):
        # TODO: добавить поле description
        try:
            detail = re.findall(r'((\d*\,?)(\".*[^\)]))', error.args[0])
            detail = re.findall(r'[\w\s]*\'[\w]*\'', detail[0][0])
            detail = detail[0]
        except:
            detail = "No Details for Error"
        return status.HTTP_409_CONFLICT, message(message=detail)
    if isinstance(error, DataError):
        detail = re.findall(r"\"(.*)\"", error.args[0])
        return status.HTTP_400_BAD_REQUEST, message(message="Данные не корректны", description='', status="fail", data=[])
    if isinstance(error, ConnectionClosedError):
        return message(message="Данные не обнаружены", description='', status="fail", data=[])
    if isinstance(error, JSONDecodeError):
        return message(message="Данные не обнаружены", description='', status="fail", data=[])
    raise error

def message(message, description=None, **kwargs):
    result = {
        "message": str(message)
    }
    if description is not None:
        result["description"] = description
    if kwargs:
        for key, value in kwargs.items():
            result[key] = value
    return result

def parse_params_num(params: str) -> set:
    reg = re.findall(r'[0-9]{1,}', params)
    result = {*reg}
    return result

async def read_from_socket(websocket: WebSocket, queue: Queue):
    async for data in websocket.iter_json():
        print(data)
        queue.put_nowait(data)

def convert_second_to_time(seconds: int) -> str:
    s = seconds % (24 * 3600)
    h = s // 3600
    s %= 3600
    m = s // 60
    s = s % (24 * 3600)
    s %= 60
    return str("%02d:%02d:%02d" % (h, m, s))

def convert_time_to_second(input_time: time) -> int:
    return (input_time.hour * 60 + input_time.minute) * 60 + input_time.second