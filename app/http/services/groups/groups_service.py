from app.database import GroupsRepository


class GroupsService:
    def __init__(self, groups_repository: GroupsRepository) -> None:
        self._repository: GroupsRepository = groups_repository
    def get_all(self):
        return self._repository.get_all()