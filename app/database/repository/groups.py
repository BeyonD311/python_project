from .super import SuperRepository, NotFoundError
from app.database import GroupsModel

class GroupsRepository(SuperRepository):
    base_model = GroupsModel
    ...


__all__ = ('GroupsRepository')