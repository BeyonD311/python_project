import datetime
from .super import SuperRepository, NotFoundError
from app.database.models import RolesModel, PermissionsAccessModel, RolesPermission

class RolesRepository(SuperRepository):
    base_model = RolesModel

    def get_all(self):
        with self.session_factory() as session:
            return session.query(self.base_model).filter(self.base_model.is_active == True).all()
    def get_all_modules(self):
        with self.session_factory() as session:
            return session.query(PermissionsAccessModel).all()
    def add(self, params):
        with self.session_factory() as session:
            role = RolesModel(
                name = params.name
            )
            self.role_create(params=params, session=session, role=role)
            return role

    def update(self, params):
        with self.session_factory() as session:
            role = session.query(self.base_model).filter(self.base_model.id == params.id).first()
            if role == None:
                raise NotFoundError(params.id)
            role.permissions.clear()
            self.role_create(role=role, session=session, params=params)
            return role

    def role_create(self, params, session, role):
        print("---------------------")
        access_right = {}
        for modules in params.modules:
            modul = session.query(PermissionsAccessModel).filter(PermissionsAccessModel.id == modules.id).first()
            permission = modules.access 
            permission_right = f"{int(permission.create)}{int(permission.read)}{int(permission.update)}{int(permission.delete)}"
            access_right[modules.id] = permission_right
            role.permissions.append(modul)
        session.add(role)
        session.commit()
        for module_id in access_right:
            access = access_right[modules.id]
            role_permission = session.query(RolesPermission).filter(RolesPermission.module_id == module_id).filter(RolesPermission.role_id == role.id).first()
            role_permission.method_access = access
            session.add(role_permission)
            session.commit()
        print("---------------------")