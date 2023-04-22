from .super import SuperRepository, NotFoundError
from app.database.models import RolesPermission

class RolesPermissionRepository(SuperRepository):

    base_model = RolesPermission

    def get_by_id(self, id: int):
        with self.session_factory as session:
            permissions = session.query(self.base_model).filter(self.base_model.role_id == id).all()
            print(permissions)
            return 123

    def add():
        pass
    def update():
        pass