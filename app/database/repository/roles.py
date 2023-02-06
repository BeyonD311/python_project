import datetime
from .super import SuperRepository, NotFoundError
from app.database.models import RolesModel

class RolesRepository(SuperRepository):
    base_model = RolesModel

    def get_all(self):
        return super().get_all()

    def add():
        pass
    def update():
        pass