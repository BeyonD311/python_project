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
            else: 
                position = None
            if user.deparment is not None:
                deparment = user.deparment.name
            else:
                deparment = None
            
            user = UserResponse(
                id = user.id, 
                fio = user.fio,
                inner_phone = user.inner_phone,
                deparment = deparment,
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

    def find_user_by_login(self, login: str):
        return self._repository.get_by_login(login)

    def create_user(self, user: UserRequest) -> any:
        user_create = self._repository.add(self.__fill_fields(user))
        return user_create
    
    def update_user(self, user: UserRequest) -> any:
        return self._repository.update(self.__fill_fields(user))

    def delete_user_by_id(self, user_id: int) -> None:
        return self._repository.delete_by_id(user_id)
    
    def __save_file(self, image) -> str:
        chuck_size = 4000
        file_name = image.filename.replace(" ", "_")
        output_file = f"/app/images/user_image/{file_name}"
        if os.path.isfile(output_file):
            os.remove(output_file)
        file = open(output_file, "wb+")
        data = image.file.read(chuck_size)
        while(data != b''):
            file.write(data)
            data = image.file.read(chuck_size)
        image.close()
        file.close()
        return output_file
    
    def __fill_fields(self, user: UserRequest):
        user_create = UserModel()
        user_fields = user.__dict__
        if user.image is not None:
            user_create.photo_path = self.__save_file(user.image)
        for field in user_fields:
            user_create.__setattr__(field, user_fields[field])
        user_create.hashed_password = sha256(user.password.encode()).hexdigest()
        return user_create


__all__ = ('UserService')