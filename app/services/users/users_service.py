from uuid import uuid4
from typing import Iterator
from database import UserRepository, UserModel


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    def get_users(self) -> Iterator[UserModel]:
        return self._repository.get_all()

    def get_user_by_id(self, user_id: int) -> UserModel:
        return self._repository.get_by_id(user_id)

    def create_user(self) -> UserModel:
        uid = uuid4()
        return self._repository.add(email=f"{uid}@email.com", password="pwd")

    def delete_user_by_id(self, user_id: int) -> None:
        return self._repository.delete_by_id(user_id)