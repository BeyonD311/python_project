from .super import SuperRepository, NotFoundError
from app.database.models import GroupsModel

class GroupsRepository(SuperRepository):
    base_model = GroupsModel
    def add(self, arg):
        pass
    def update(self):
        pass


__all__ = ('GroupsRepository')