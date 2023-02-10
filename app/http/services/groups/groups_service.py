from app.database import GroupsRepository


class GroupsService:
    def __init__(self, goups_repository: GroupsRepository) -> None:
        self._repository: GroupsRepository = goups_repository
    def get_all(self):
        return self._repository.get_all()