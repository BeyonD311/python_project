from contextlib import AbstractContextManager
from typing import Callable
from abc import ABC, abstractmethod
from math import ceil
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

class Pagination(BaseModel):
    total_count: int
    page: int
    total_page: int
    size: int
    def toJSON(self):
        return json.dumps(self.__dict__)


class SuperRepository(ABC):
    base_model = None

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def get_all(self):
        with self.session_factory() as session:
            return session.query(self.base_model).all()
    
    def get_by_id(self, id: int):
        with self.session_factory() as session:
            user = session.query(self.base_model).filter(self.base_model.id == id).first()
            self._error_not_found(user,id)
            return user

    def delete_by_id(self, id: int) -> None:
        with self.session_factory() as session:
            entity: self.base_model = session.query(self.base_model).filter(self.base_model.id == id).first()
            if not entity:
                raise NotFoundError(entity_id=id)
            session.delete(entity)
            session.commit()

    def get_pagination(self, query, size: int, page: int):
        count_items = query.count()
        total_page = ceil(count_items / size)
        return {
            "pagination": Pagination(
                total_page = total_page,
                total_count = count_items,
                page=page,
                size=size
            )
        }

    def soft_delete(self, id: int):
        with self.session_factory() as session:
            entity: self.base_model = session.query(self.base_model).filter(self.base_model.id == id).first()
            if not entity:
                raise NotFoundError(entity_id=id)
            entity.is_active = False
            session.add(entity)
            session.commit()

    def _error_not_found(self, entity, id):
        if entity is None:
            raise NotFoundError(entity_id=id)

    @abstractmethod
    def add(self, arg):
        pass

    @abstractmethod
    def update(self):
        pass


class BaseException(Exception):
    message_err: str = "An unknown exception occurred."
    description_err: str = "Неопределённое описание ошибки."
    code_err: int = 500

    def __init__(self,
            item: str = None,
            entity_id: int = None,
            entity_message: str = None,
            entity_description: str = None
        ) -> None:
        """Инициализация объекта исключения

        :param item: значение, которое привело к ошибке, defaults to None
        :type item: str, optional
        :param entity_id: номер, который привел к ошибке, defaults to None
        :type entity_id: int, optional
        :param entity_message: логгируемое сообщение, defaults to None
        :type entity_message: str, optional
        :param entity_description: отображаемое сообщение, defaults to None
        :type entity_description: str, optional
        """

        self.item = item
        self.entity_id = entity_id
        self.http_code = self.code_err
        self.message = entity_message if entity_message is not None else self.message_err
        self.description = entity_description if entity_description is not None else self.description_err

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