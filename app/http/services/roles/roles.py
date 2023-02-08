from app.database import RolesRepository, RolesModel, RolesPermissionRepository

class RolesServices():
    def __init__(self, roles_repository: RolesRepository) -> None:
        self._repository = roles_repository
    def get_all(self):
        return self._repository.get_all()

class RolesPermission:
    def __init__(self, roles_repository: RolesPermissionRepository) -> None:
        self._repository = roles_repository
    def get_permission(self, id: int):
        return self._repository.get_by_id(id)