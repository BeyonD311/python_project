import re
from pydantic import BaseModel
from fastapi import status
from .logger_default import get_logger
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from fastapi import status

logger = get_logger("Error.log")

class BaseException(Exception):

    """ Super Class Exceptions 
        Базовый класс для 
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self,message: str, description: str) -> None:
        """  """
        self.message = message
        self.description = description
        super().__init__(message, description)
    def __str__(self):
        return self.message

class NotFoundError(BaseException):
    status_code = status.HTTP_404_NOT_FOUND


class ExpectationError(BaseException):
    """Не удаётся обработать данные в запросе.
    """
    status_code = status.HTTP_400_BAD_REQUEST


class AccessException(BaseException):
    """
        Недостаточно прав доступа.
    """
    code_err: int = status.HTTP_403_FORBIDDEN


class RequestException(BaseException):
    """
        Неверные параметры запроса.
    """
    code_err: int = status.HTTP_400_BAD_REQUEST

class ExistsException(RequestException):
    ...

class UnauthorizedException(BaseException):
    """Отсутствуют действительные учетные данные для проверки подлинности.
    """

class UserIsFired(UnauthorizedException):
    ...


class ResponseException(BaseModel):
    message: str
    description: str = None

# Ошибки в бд
DB_EXCEPTIONS = (IntegrityError)

def _converting_exception_message(args: tuple) -> ResponseException:
    message = args[0]
    if re.search(r'^\([a-z\.0-9A-Z]*\)', args[0]):
        message = re.sub(r'^\([a-z\.0-9A-Z]*\)', "", args[0])
        split = message.split("\n")
        message = split.pop(-2)
    return ResponseException(message=message, description=args[1])

def exceptions_handling(exception: Exception) -> JSONResponse:
    """ Функция преобразования обработанных ошибок """
    arguments = ("exception not handled", "Динамическое исключение")
    if len(exception.args) == 1:
        arguments = (exception.args[0], "Динамическое исключение")
    elif len(exception.args) > 2:
        arguments = exception.args
    code = status.HTTP_400_BAD_REQUEST
    if isinstance(exception, DB_EXCEPTIONS):
        code = status.HTTP_502_BAD_GATEWAY
        arguments = (exception.args[0], "Ошибка целостности данных")
    elif isinstance(exception, BaseException):
        code = exception.status_code
    else:
        logger.exception(exception)
        raise exception
    return JSONResponse(status_code=code, content=_converting_exception_message(arguments).dict())
