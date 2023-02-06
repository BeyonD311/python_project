from .super import SuperRepository, NotFoundError
from app.database.models import GroupsModel

class GroupsRepository(SuperRepository):
    base_model = GroupsModel
    ...


__all__ = ('GroupsRepository')