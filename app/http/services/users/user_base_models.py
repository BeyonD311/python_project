from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import List
from datetime import datetime
from app.http.services.dto import BaseDTO
from app.database.repository.super import Pagination

class UserLoginParams(BaseModel):
    login: str
    password: str

class UserStatus(BaseModel):
    status: str = None
    status_id: int = None
    status_at: datetime = None
    color: str = None

""" Поля пользователя """
class UsersResponse(BaseModel):
    id: int = None
    fio: str = None
    inner_phone: int = None
    deparment: str = None
    position: str = None
    is_head_of_depatment: bool = False
    status: UserStatus = None


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
    deparment: str = None
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
    head_of_depatment: bool
    deputy_head: bool

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

class UserParams(BaseModel):
    page: int
    size: int
    sort_field: str
    sort_dir: str 
    filter: UsersFilter = None