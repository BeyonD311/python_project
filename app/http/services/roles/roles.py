from app.database import RolesRepository, RolesModel, RolesPermissionRepository
from app.http.services.helpers import parse_access, BaseAccess
from app.http.services.roles.roles_base_model import Create, Update

class RolesServices():
    def __init__(self, roles_repository: RolesRepository) -> None:
        self._repository = roles_repository
    def get_all(self):
        roles = self._repository.get_all()
        result = []
        for role in roles:
            role_res = {
                "id": role.id,
                "name": role.name,
                "access": []
            }
            modules = {r.id:r for r in role.permissions}
            res = []
            for access in role.permission_model:
                if access.module_id in modules:
                    parse = parse_access(access.method_access)
                    module = {
                        "id": modules[access.module_id].id,
                        "module_name": modules[access.module_id].module_name,
                        "name": modules[access.module_id].name,
                        "access": {
                            "create": parse.create,
                            "read": parse.read,
                            "update": parse.update,
                            "delete": parse.delete
                        }
                    }
                    role_res['access'].append(module)
            result.append(role_res)
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