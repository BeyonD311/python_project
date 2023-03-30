from .super import SuperRepository, NotFoundError
from app.database.models import RolesModel, PermissionsAccessModel, RolesPermission, UserRoles
from sqlalchemy import case, literal_column
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session

class RolesRepository(SuperRepository):
    base_model = RolesModel

    def get_all(self):
        with self.session_factory() as session:
            modules = self.__permission_default(session)
            roles = self.__query_all(session).order_by(RolesModel.id.asc())
            return self.__parse_role(modules=modules,roles=roles)
    def get_by_id(self, id: int):
        with self.session_factory() as session:
            modules = self.__permission_default(session)
            current_role = self.__query_all(session).filter(RolesModel.id == id).all()
            return self.__parse_role(modules=modules,roles=current_role)
        
    def get_all_modules(self):
        with self.session_factory() as session:
            return session.query(PermissionsAccessModel).all()
    def add(self, params):
        with self.session_factory() as session:
            role = RolesModel(
                name = params.name
            )
            self.role_create(params=params, session=session, role=role)

    def update(self, params):
        with self.session_factory() as session:
            role = session.query(self.base_model).filter(self.base_model.id == params.id).first()
            if role == None:
                raise NotFoundError(params.id)
            role.permissions.clear()
            role.name = params.name
            self.role_create(role=role, session=session, params=params)
            return role

    def role_create(self, params, session, role):
        access_right = {}
        for modules in params.modules:
            modul = session.query(PermissionsAccessModel).filter(PermissionsAccessModel.id == modules.id).first()
            permission = modules.access 
            permission_right = f"{int(permission.create)}{int(permission.read)}{int(permission.update)}{int(permission.delete)}{int(permission.personal)}"
            access_right[modules.id] = permission_right
            role.permissions.append(modul)
        session.add(role)
        session.commit()
        role_permission = session.query(RolesPermission).filter(RolesPermission.role_id == role.id).all()
        for permission in role_permission:
            if permission.module_id in access_right:
                permission.method_access = access_right[permission.module_id]
                session.add(permission)
        session.commit()
    def __query_all(self, session: Session) -> Query:
        return session.query(
            PermissionsAccessModel.module_name, 
            PermissionsAccessModel.name, 
            RolesPermission.method_access, 
            RolesPermission.role_id, 
            PermissionsAccessModel.id,
            RolesModel.name
        )\
        .join(RolesPermission, RolesPermission.module_id == PermissionsAccessModel.id)\
        .join(RolesModel, RolesModel.id == RolesPermission.role_id)\
        .filter(RolesPermission.is_active == True, RolesPermission.is_available == True)

    def __permission_default(self, session: Session):
        query = session.query(PermissionsAccessModel.id, PermissionsAccessModel.module_name, PermissionsAccessModel.name).all()
        result = {}
        permission:PermissionsAccessModel
        for permission in query:
            result[permission.id] = {
                "module_name": permission.module_name,
                "name": permission.name,
                "method_access": "00000"
            }
        return result

    def __parse_role(self, modules, roles):
        result = {}
        for role in roles:
            if role[3] not in result:
                result[role[3]] = {
                    'id': role[3],
                    'name': role[5],
                    'access': {}
                }
            result[role[3]]['access'][role[4]] = {
                    "id": role[4],
                    "module_name": role[0],
                    "name": role[1],
                    "method_access": role[2]
                }
        for role_id, item in result.items():
            for module_id in modules:
                if module_id not in item['access']:
                    item['access'][module_id] = modules[module_id]
        return result
        