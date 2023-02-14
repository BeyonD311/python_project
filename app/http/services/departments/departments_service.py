from app.database import DeparmentsRepository
from pydantic import BaseModel
from typing import List

class DepartmentParams(BaseModel):
    name: str
    department_id: int = None
    director_user_id: int
    deputy_head_id: List[int] = None

class DepartmentsService:

    def __init__(self, repository: DeparmentsRepository) -> None:
        self._repository: DeparmentsRepository = repository

    def get_all(self):
        return self._repository.get_all()

    def add(self, params: DepartmentParams):
        self._repository.add(params)