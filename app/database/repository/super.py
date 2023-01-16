from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

class SuperRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

class NotFoundError(Exception):
    entity_name: str
    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")