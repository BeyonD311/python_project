from fastapi import status

class BaseException(Exception):

    """ Super Class Exceptions 
        Базовый класс для 
    """

    def __init__(self,
            message: str,
            description: str
        ) -> None:
        """  """
        self.message = message
        self.description = description
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    def __str__(self):
        return self.message


class NotFoundError(BaseException):
    message_err: str = "Unable to find the resource"
    code_err: int = 404

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if 'item' in kwargs:
            self.message = f"{self.message_err} with value '{kwargs['item']}'"
        elif 'entity_id' in kwargs:
            self.message = f"{self.message_err} with id={kwargs['entity_id']}"


class UserNotFoundError(NotFoundError):
    message_err: str = "User could not be found"
    code_err: int = 404

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class ExpectationError(BaseException):
    """Не удаётся обработать данные в запросе.
    """
    message_err: str = ""
    code_err = 417

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class AccessException(BaseException):
    """Недостаточно прав доступа.
    """
    message_err: str = "Access Forbidden."
    code_err: int = 403

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> None:
        super().__str__()


class RequestException(BaseException):
    """Неверные параметры запроса.
    """
    message_err: str = ""
    code_err: int = 400

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class BadFileException(RequestException):
    """Неверный формат загружаемого файла.
    """
    message_err: str = "Invalid format of the uploaded file"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if 'item' in kwargs:
            self.message = f"{self.message_err} with name '{kwargs['item']}'"
        elif 'entity_id' in kwargs:
            self.message = f"{self.message_err} with id={kwargs['entity_id']}"


class ExistsException(RequestException):
    """Поле или объект уже существует.
    """
    message_err: str = "Resource already exists"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if 'item' in kwargs:
            self.message = f"{self.message_err} with name '{kwargs['item']}'"
        elif 'entity_id' in kwargs:
            self.message = f"{self.message_err} with id={kwargs['entity_id']}"


class UnauthorizedException(BaseException):
    """Отсутствуют действительные учетные данные для проверки подлинности.
    """
    code_err = 401

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

class UserIsFired(UnauthorizedException):
    def __init__(self) -> None:
        message = "The user is fired"
        description = "Пользователь уволен"
        super().__init__(entity_message=message, entity_description=description)