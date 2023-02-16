import os
from hashlib import sha256
from app.database import UserModel, UserRepository, NotFoundError, SkillsRepository
from app.http.services.users.user_base_models import UserResponse, ResponseList, UserRequest, UserParams


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repository: UserRepository = user_repository

    def get_all(self, params: UserParams) -> ResponseList:
        result = self._repository.get_all(params)
        users = []
        for user in result['items']:
            status_at = user[7]
            if status_at is not None:
                status_at = user[7].timestamp()
            user = UserResponse(
                id = user[0], 
                fio = user[1],
                inner_phone = user[4],
                deparment = user[2],
                position = user[3],
                status=user[5],
                status_id=user[6],
                status_at=status_at
            )
            users.append(user)
        return ResponseList(pagination = result['pagination'], users = users)

    def get_user_by_id(self, user_id: int, show_pass: bool = False):
        user = self._repository.get_by_id(user_id)
        user.deparment
        user.position
        user.groups
        for skill in user.skills:
            skill
        for role in user.roles:
            role
        if show_pass == False:
            if "password" in user.__dict__:
                user.__delattr__("password")
                user.__delattr__("hashed_password")
        return self._repository.get_by_id(user_id)

    def find_user_by_login(self, login: str):
        return self._repository.get_by_login(login)

    def create_user(self, user: UserRequest) -> any:
        user_create = self._repository.add(self.__fill_fields(user))
        return user_create
    
    def update_user(self, user: UserRequest) -> any:
        if user.id == 0:
            raise NotFoundError(user.id)
        return self._repository.update(self.__fill_fields(user))

    def delete_user_by_id(self, user_id: int) -> None:
        if user_id == 0:
            raise NotFoundError(user_id)
        return self._repository.soft_delete(user_id)
    
    def get_all_status_users(self):
        return self._repository.get_all_status()

    def set_status(self, user_id: int, status_id: int):
        self._repository.set_status(user_id=user_id, status_id=status_id)

    def add_skill(self, text: str):
        return self._repository.add_skill(text)

    def find_skill(self, text: str):
        return self.find_skill(text)

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
            if field == "image":
                continue
            user_create.__setattr__(field, user_fields[field])
        user_create.hashed_password = sha256(user.password.encode()).hexdigest()
        return user_create

class SkillService:
    def __init__(self, skill_repository: SkillsRepository) -> None:
        self._repository: SkillsRepository = skill_repository
    
    def add(self, text: str):
        return self._repository.add_skill(text)
    
    def find(self, text:str):
        return self._repository.find_skill(text)

__all__ = ('UserService', 'SkillsRepository')