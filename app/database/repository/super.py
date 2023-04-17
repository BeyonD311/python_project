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
                raise NotFoundError(id)
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
                raise NotFoundError(id)
            entity.is_active = False
            session.add(entity)
            session.commit()
    
    def _error_not_found(self, entity, id):
        if entity is None:
            raise NotFoundError(id)

    @abstractmethod
    def add(self, arg):
        pass

    @abstractmethod

    def update(self):
        pass


class NotFoundError(Exception):
    entity_name: str
    def __init__(self, entity_id):
        super().__init__(f"not found, id: {entity_id}")
