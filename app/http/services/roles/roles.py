from app.database.repository.roles import RolesRepository
from app.database.models import RolesModel

class RolesServices():
    def __init__(self, roles_repository: RolesRepository) -> None:
        self._repository = roles_repository
    def get_all(self):
        return self._repository.get_all()