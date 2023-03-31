from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.database.repository.super import Pagination
from app.http.services.access import BaseAccess

class UserLoginParams(BaseModel):
    login: str
    password: str

class UserStatus(BaseModel):
    status: str = None
    status_id: int = None
    status_at: datetime = None
    color: str = None

class UserPosition(BaseModel):
    id: int
    name: str

class UserDepartment(BaseModel):
    id: int
    name: str

""" Поля пользователя """
class UsersResponse(BaseModel):
    id: int = None
    fio: str = None
    inner_phone: int = None
    department: str = None
    position: str = None
    is_head_of_department: bool = False
    employment_status: bool
    status: UserStatus = None

class Permission(BaseModel):
    name: str
    module_id: int
    module_name: str
    method_access: BaseAccess

class Role(BaseModel):
    id: int
    role_name: str
    permissions: List[Permission]

class UserPermission(BaseModel):
    user_id: int
    role: List[Role]

class UserDetailResponse(BaseModel):
    id: int
    email: str
    name: str
    last_name: str
    patronymic: str = None
    login: str
    fio: str
    inner_phone: int = None
    phone: str = None
    department: dict = None
    position: dict = None
    groups: list = None
    skills: list = None
    roles: list = None
    image_id: int = None
    status: UserStatus = None
    personal_number: str = None
    password: str
    photo_path: str = None
    is_operator: bool = None
    date_employment_at: datetime = None
    date_dismissal_at: datetime = None
    employment_status: bool

class UserRequest(BaseModel):
    email: str = None
    password: str = None
    name: str
    last_name: str
    patronymic: str = None
    login: str
    is_operator: bool
    phone: str = None
    inner_phone: int = None
    image_id: int = None
    department_id: int = None
    personal_number: str = None 
    position_id: int
    group_id: list[int]
    roles_id: list[int]
    skills_id: list[int] = []
    date_employment_at: datetime = None

class ResponseList(BaseModel):
    pagination: Pagination
    users: list[UsersResponse]

class UsersFilter(BaseModel):
    fio: str = None
    login: str = None
    status: list[int] = None
    department: int = None 

class UserParams(BaseModel):
    page: int
    size: int
    sort_field: str
    sort_dir: str 
    filter: UsersFilter = None