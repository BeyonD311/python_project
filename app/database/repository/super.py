from contextlib import AbstractContextManager
from typing import Callable
from abc import ABC, abstractmethod
from math import floor
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
            if not user:
                raise NotFoundError(id)
            return user

    def delete_by_id(self, id: int) -> None:
        with self.session_factory() as session:
            entity: self.base_model = session.query(self.base_model).filter(self.base_model.id == id).first()
            if not entity:
                raise NotFoundError(id)
            session.delete(entity)
            session.commit()
    def get_pagination(self, session: Session, page: int, size: int) -> dict[Pagination]:
        count_items = session.query(self.base_model).count()
        total_page = floor(count_items / size)
        return {
            "pagination": Pagination(
                total_page = total_page,
                total_count = count_items,
                page=page + 1,
                size=size
            )
        }
    @abstractmethod
    def add(self, arg):
        pass

    @abstractmethod

    def update(self):
        pass
    


class NotFoundError(Exception):
    entity_name: str
    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")