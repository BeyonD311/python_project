from uuid import uuid4
from typing import Iterator
import re
from pydantic import EmailStr

from app.database.repository.users import UserRepository
from app.database.models.users import UserModel

from email_validator import validate_email, EmailNotValidError


def check_if_email(user_login) -> bool:
    try:
        validate_email(user_login)
        return True
    except EmailNotValidError as e:
        print(str(e))
        return False


def check_new_login(user_login: str) -> bool:
    return re.match(r'^\w+$', user_login)


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    def get_users(self) -> Iterator[UserModel]:
        return self._repository.get_all()

    def get_user_by_id(self, user_id: int) -> UserModel:
        return self._repository.get_by_id(user_id)

    def check_user(self, user_email: EmailStr, user_name: str):
        return True if (self._repository.check_user_name(user_name) is True or
                        self._repository.check_user_email(user_email) is True) else False

    def check_login(self, user_login: str):
        return self._repository.check_user(user_login, check_if_email(user_login))

    def create_user(self, user_name: str, user_email: EmailStr, user_password: str) -> UserModel:
        uid = uuid4()
        return self._repository.add(user_name, user_email, user_password)

    def delete_user_by_id(self, user_id: int) -> None:
        return self._repository.delete_by_id(user_id)

    def get_hashed_password(self, user_login):
        return self._repository.get_hashed_password(user_login, check_if_email(user_login))

    def return_user_id(self, user_login: str):
        return self._repository.return_user_id(user_login, check_if_email(user_login))

    @staticmethod
    def validate_new_login(user_login: str) -> bool:
        return check_new_login(user_login)

    @staticmethod
    def validate_new_email(user_email: str) -> bool:
        return check_if_email(user_email)
