from .super import SuperRepository, NotFoundError
from app.database.models import DepartmentsModel
from typing import Iterator

class DeparmentsRepository(SuperRepository):
    def get_all(self) -> Iterator[DepartmentsModel]:
        with self.session_factory() as session:
            return session.query(DepartmentsModel).all()
    def get_by_id(self, department_id: int) -> DepartmentsModel:
        with self.session_factory() as session:
            department = session.query(DepartmentsModel).filter(DepartmentsModel.id == department_id).first()
            if not department:
                raise DeparmentNotFound(department_id)
            return department

class DeparmentNotFound(NotFoundError):
    entity_name: str = "department"
