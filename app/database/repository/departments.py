from .super import SuperRepository, NotFoundError
from app.database.models import DepartmentsModel
from typing import Iterator

class DeparmentsRepository(SuperRepository):

    base_model = SuperRepository

    def get_all(self) -> Iterator[DepartmentsModel]:
        return super().get_all()
    def get_by_id(self, department_id: int) -> DepartmentsModel:
        return super().get_by_id(department_id)

class DeparmentNotFound(NotFoundError):
    entity_name: str = "department"
