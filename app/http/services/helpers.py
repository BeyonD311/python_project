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


class ProjectExceptionsImport:
    """Класс содержит в импортах все исключения проекта, которые
    необходимо отлавливать в контроллерах -> app\http\controllers.
    # TODO: вынести класс в отдельный модуль обработки ошибок.

    Работа с объектом класса, чтобы получить массив исключений:
        project_exceptions = ProjectExceptionsImport()
        exceptions_array: tuple[str] = tuple(project_exceptions.__dir__())
    """
    from app.database.repository.super import (
        NotFoundError, ExpectationError, ExistsException, AccessException,
        RequestException, BadFileException, UserNotFoundError
    )


def default_error(error: Exception, source=None):
    project_exceptions = ProjectExceptionsImport()
    exceptions_array: tuple = tuple(project_exceptions.__dir__())
    name_err = error.__repr__().split('(')[0]
    if name_err == "IntegrityError":
        try:
            detail = re.findall(r'((\d*\,?)(\".*[^\)]))', error.args[0])
            detail = re.findall(r'[\w\s]*\'[\w]*\'', detail[0][0])
            detail = detail[0]
        except:
            detail = "No Details for Error"
        description = "Ошибка целостности БД"
        return status.HTTP_409_CONFLICT, message(source, message=detail, description=description)
    if name_err == "DataError":
        detail = re.findall(r"\"(.*)\"", error.args[0])
        description = "Данные не корректны"
        return status.HTTP_400_BAD_REQUEST, message(source, message=detail, description='')
    if name_err == "JSONDecodeError":
        err_message = "JSON data is not formatted."
        description = "Данные не обнаружены"
        return message(source, message=err_message, description=description)
    if name_err in exceptions_array:  # NOTE: Custom project exceptions
        return error.http_code, message(source, message=error, description=error.description)
    raise error


def message(source, message, description=None, **kwargs):
    result = {
        "message": f"{source}: {str(message)}"
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