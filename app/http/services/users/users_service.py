from uuid import uuid4
from app.database import UserRepository, UserModel
from datetime import datetime

class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    def get_all(self, offset: int = 1, limit: int = 100):
        result = self._repository.get_all(offset, limit)
        for user in result['items']:
            del user.hashed_password
            user.deparment
            user.roles
            user.position
            user.group_user
        return result

    def get_user_by_id(self, user_id: int) -> UserModel:
        return self._repository.get_by_id(user_id)

    def create_user(self) -> UserModel:
        uid = uuid4()
        return self._repository.add(
            email=f"{uid}@email.com", 
            password="pwd", login = "test",
            name = "test name", 
            last_name = "test last name", 
            department_id = 1,
            date_employment_at = datetime.now(),
        )

    def delete_user_by_id(self, user_id: int) -> None:
        return self._repository.delete_by_id(user_id)

__all__ = ('UserService')