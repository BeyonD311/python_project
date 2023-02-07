import os
from hashlib import sha256
from app.database import UserModel, DepartmentsModel, UserRoles, UserRepository
from app.http.services.users.user_base_models import UserResponse, ResponseList, UserRequest
from sqlalchemy.exc import IntegrityError


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

    def create_user(self, user: UserRequest) -> any:
        
        user_create = UserModel()
        if user.image is not None:
            chuck_size = 4000
            file_name = user.image.filename.replace(" ", "_")
            output_file = f"/app/images/user_image/{file_name}"
            if os.path.isfile(output_file):
                os.remove(output_file)
            file = open(output_file, "wb+")
            data = user.image.file.read(chuck_size)
            while(data != b''):
                file.write(data)
                data = user.image.file.read(chuck_size)
            user.image.close()
            file.close()
            user_create.photo_path = output_file
        user_create.hashed_password = sha256(user.password.encode()).hexdigest()
        user_create.department_id = user.deparment_id
        user_create.position_id = user.position_id
        user_create.name = user.name
        user_create.last_name = user.last_name
        user_create.patronymic = user.patronymic
        user_create.inner_phone = user.inner_phone
        user_create.login = user.login
        user_create.password = user.password
        user_create.email = user.email
        user_create.phone = user.phone
        user_create.date_employment_at = user.date_employment_at
        user_create.roles_id = user.roles_id
        user_create.fio = user.fio


        user_create = self._repository.add(user_create)
        return user_create
    
    def update_user(self, user: UserRequest) -> any:
        user_create = UserModel()
        user_create.id = user.id
        if user.image is not None:
            chuck_size = 4000
            file_name = user.image.filename.replace(" ", "_")
            output_file = f"/app/images/user_image/{file_name}"
            if os.path.isfile(output_file):
                os.remove(output_file)
            file = open(output_file, "wb+")
            data = user.image.file.read(chuck_size)
            while(data != b''):
                file.write(data)
                data = user.image.file.read(chuck_size)
            user.image.close()
            file.close()
            user_create.photo_path = output_file
        user_create.hashed_password = sha256(user.password.encode()).hexdigest()
        user_create.department_id = user.deparment_id
        user_create.position_id = user.position_id
        user_create.name = user.name
        user_create.last_name = user.last_name
        user_create.patronymic = user.patronymic
        user_create.inner_phone = user.inner_phone
        user_create.login = user.login
        user_create.password = user.password
        user_create.email = user.email
        user_create.phone = user.phone
        user_create.date_employment_at = user.date_employment_at
        user_create.roles_id = user.roles_id
        user_create.fio = user.fio
        return self._repository.update(user_create)

    def delete_user_by_id(self, user_id: int) -> None:
        return self._repository.delete_by_id(user_id)

__all__ = ('UserService')