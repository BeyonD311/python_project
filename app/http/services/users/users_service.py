from hashlib import sha256
from app.database.repository import UserRepository
from app.database import UserModel, DepartmentsModel
from app.http.services.users.user_base_models import UserResponse, ResponseList, UserRequestCreateUser

class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    def get_all(self, offset: int = 1, limit: int = 10) -> ResponseList:
        result = self._repository.get_all(offset, limit)
        users = []
        for user in result['items']:
            user.deparment
            position = None
            if user.position is not None:
                position = user.position.name
            user = UserResponse(
                id = user.id, 
                name = user.name, 
                last_name = user.last_name, 
                patronymic = user.patronymic,
                inner_phone = user.inner_phone,
                deparment = user.deparment.name,
                position = position
            )
            users.append(user)
        return ResponseList(pagination = result['pagination'], users = users)

    def get_user_by_id(self, user_id: int, show_pass: bool = False):
        user = self._repository.get_by_id(user_id)
        user.deparment
        user.roles
        user.position
        user.group_user
        if show_pass == False:
            user.__delattr__("password")
            user.__delattr__("hashed_password")
        return self._repository.get_by_id(user_id)

    def create_user(self, user: UserRequestCreateUser) -> any:
        user_create = UserModel()
        user_create.hashed_password = sha256(user.password.encode()).hexdigest()
        user_create.department_id = user.deparment_id
        user_create.position_id = user.position_id
        user_create.name = user.name
        user_create.last_name = user.last_name
        user_create.patronymic = user.patronymic
        user_create.photo_path = user.photo_path
        user_create.inner_phone = user.inner_phone
        user_create.login = user.login
        user_create.password = user.password
        user_create.date_employment_at = user.date_employment_at
        # user_create.roles = user.roles_id
        return self._repository.add(user_create)

    def delete_user_by_id(self, user_id: int) -> None:
        return self._repository.delete_by_id(user_id)

__all__ = ('UserService')