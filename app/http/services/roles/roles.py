from app.database import RolesRepository, RolesModel, RolesPermissionRepository
from app.http.services.access import Access, BaseAccess
from app.http.services.roles.roles_base_model import Create, Update

class RolesServices():
    def __init__(self, roles_repository: RolesRepository) -> None:
        self._repository = roles_repository

    def get(self, id: int = None):
        if id is not None:
            roles = self._repository.get_by_id(id)
        else:
            roles = self._repository.get_all()
        access = Access()
        result = []
        for role_id, role in roles.items():
            res = []
            for module_id, module in role['access'].items():
                access.parse(module['method_access'])
                res.append({
                    'name': module['name'],
                    'module_name': module['module_name'],
                    'access': access.get_access_model()
                })
            role['access'] = res
            result.append(role)
        return result
    def get_modules(self):
        modules = self._repository.get_all_modules()
        for m in modules:
            m.access = BaseAccess()
        return self._repository.get_all_modules()

    def create(self, params: Create):
        return self._repository.add(params)

    def update(self, params: Update):
        return self._repository.update(params)
    
    def delete(self, id: int):
        return self._repository.delete_by_id(id)

class RolesPermission:
    def __init__(self, roles_repository: RolesPermissionRepository) -> None:
        self._repository = roles_repository
    def get_permission(self, id: int):
        return self._repository.get_by_id(id)