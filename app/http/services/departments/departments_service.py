from app.database import DeparmentsRepository

class DepartmentsService:
    def __init__(self, repository: DeparmentsRepository) -> None:
        self._repository: DeparmentsRepository = repository

    def get_all(self):
        return self._repository.get_all()