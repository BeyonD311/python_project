import datetime
import json
from hashlib import sha256
from app.database import UserModel
from app.database import UserRepository
from app.database import NotFoundError
from app.database import SkillsRepository
from app.http.services.helpers import RedisInstance
from app.http.services.users.user_base_models import UsersResponse
from app.http.services.users.user_base_models import ResponseList
from app.http.services.users.user_base_models import UserRequest
from app.http.services.users.user_base_models import UserParams
from app.http.services.users.user_base_models import UserDetailResponse
from app.http.services.users.user_base_models import UserStatus
from app.http.services.users.user_base_models import UserDepatment
from app.http.services.users.user_base_models import UserPosition

class UserService:
    def __init__(self, user_repository: UserRepository, redis: RedisInstance) -> None:
        self._repository: UserRepository = user_repository
        self._redis = redis

    def get_all(self, params: UserParams) -> ResponseList:
        result = self._repository.get_all(params)
        users = []
        for user in result['users']:
            users .append(UsersResponse(
                id=user.id,
                inner_phone=user.inner_phone,
                position=user.position,
                deparment=user.department,
                fio=user.fio,
                status=UserStatus(
                    status=user.status,
                    status_id=user.status_id,
                    status_at=user.status_at,
                    color=user.status_color
                )
            ))
        return ResponseList(pagination = result['pagination'], users = users)

    def get_user_position(self):
        return self._repository.get_users_position()

    def get_user_by_id(self, user_id: int):
        user = self._repository.get_by_id(user_id)
        userDetail = self.__user_response(user)
        password = ""
        for i in range(len(userDetail.password)):
            password += "*"
        userDetail.password = password
        del user
        return userDetail

    def by_id(self, id):
        return self._repository.get_by_id(id)

    def find_user_by_login(self, login: str):
        return self._repository.get_by_login(login) 

    def create_user(self, user: UserRequest) -> UserDetailResponse:
        user:UserDetailResponse = self.__user_response(self._repository.add(self.__fill_fields(user)))
        return user
    
    def update_user(self, id: int, user: UserRequest) -> any:
        if id == 0:
            raise NotFoundError(id)
        user = self._repository.update(id,self.__fill_fields(user))
        return self.__user_response(user)

    def delete_user_by_id(self, user_id: int) -> None:
        if user_id == 0:
            raise NotFoundError(user_id)
        return self._repository.soft_delete(user_id)
    
    def get_all_status_users(self):
        return self._repository.get_all_status()

    async def set_status(self, user_id: int, status_id: int):
        status_params = self._repository.set_status(user_id=user_id, status_id=status_id)
        await self.__set_status_redis(status_params)
            
    def dismiss(self, id: int, date_dismissal_at: datetime.datetime = None):
        if date_dismissal_at == None:
            date_dismissal_at = datetime.now()
        self._repository.user_dismiss(id, date_dismissal_at)
        return {
            "message": f"User {id} dismiss : {date_dismissal_at}"
        }
    
    def recover(self, id: int):
        self._repository.user_recover(id)
        return {
            "message": f"User {id} recover"
        }
    
    def reset_password(self, id: int, password: str):
        params = {
            "id": id,
            "password": password,
            "hashed_password": sha256(password.encode()).hexdigest()
        }
        self._repository.update_password(params=params)

        return {
            "message": "Password is update"
        }

    async def get_users_status(self, users_id: list):
        result = {}
        for user_id in users_id:
            status = await self._redis.redis.get(f"status.user.{user_id}")
            if status is not None:
                status = json.loads(status)
                result[user_id] = UserStatus(
                    user_id=user_id,
                    status_id=status['status_id'],
                    status_at=status['status_at'],
                    color=status['color'],
                    status=status['status']
                )
            result[user_id] = status
        return result

    def __fill_fields(self, user: UserRequest):
        user_create = UserModel()
        user_fields = user.__dict__
        for field in user_fields:
            if user_fields[field] == 0:
                user_fields[field] = None
            if field == "hashed_password":
                continue
            user_create.__setattr__(field, user_fields[field])
        user_create.fio = f"{user.last_name} {user.name} {user.patronymic}".strip()
        user_create.hashed_password = sha256(user.password.encode()).hexdigest()
        return user_create

    def __user_response(self, user: UserModel):
        userDetail = UserDetailResponse(
            id=user.id,
            email=user.email,
            login=user.login,
            name=user.name,
            last_name=user.last_name,
            patronymic=user.patronymic,
            fio=user.fio,
            inner_phone=user.inner_phone,
            password=user.password,
            is_operator=user.is_operator,
            date_employment_at=user.date_employment_at,
            date_dismissal_at = user.date_dismissal_at,
            phone=user.phone,
            image_id=user.image_id
        )
        userDetail.groups = user.groups
        userDetail.skills = user.skills
        userDetail.position = user.position
        status_user = user.status
        if user.position != None:
            userDetail.position = user.position
        if user.deparment != None:
            userDetail.deparment = {
                "id":user.deparment.id,
                "name":user.deparment.name
            }
        if status_user != None:
            userDetail.status = UserStatus(
                status=status_user.name,
                color=status_user.color,
                status_id=status_user.id,
                status_at=user.status_at
            )
        if user.image == None:
            userDetail.photo_path = user.image
        else:
            userDetail.photo_path = user.image.path
        for role in user.roles:
            role.permissions
        userDetail.roles = user.roles
        del status_user
        return userDetail

    async def __set_status_redis(self, status_info: dict):
        id = status_info['id']
        del status_info['id']
        await self._redis.redis.set(f"status.user.{id}", json.dumps(status_info))
            
class SkillService:
    def __init__(self, skill_repository: SkillsRepository) -> None:
        self._repository: SkillsRepository = skill_repository
    
    def add(self, text: str):
        return self._repository.add_skill(text)
    
    def find(self, text:str):
        return self._repository.find_skill(text)

__all__ = ('UserService', 'SkillsRepository')