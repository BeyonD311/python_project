from pydantic import BaseModel
from fastapi import UploadFile,File,Body,Form
from typing import List
from datetime import datetime
from app.http.services.dto import BaseDTO
from app.database.repository.super import Pagination

class UserLoginParams(BaseModel):
    login: str
    password: str

""" Поля пользователя """
class UserResponse(BaseModel):
    id: int = None
    name: str = None
    last_name: str = None
    patronymic: str = None
    inner_phone: int = None
    deparment: str = None
    position: str = None

class UserRequest(BaseModel):
    id: int = None
    email: str = None
    password: str = None
    name: str
    last_name: str
    patronymic: str = None
    fio: str
    login: str
    is_operator: bool
    phone: str = None
    inner_phone: int = None
    image: UploadFile = None
    deparment_id: int
    position_id: int
    group_id: list[int]
    roles_id: list[int]
    date_employment_at: datetime = None
    date_dismissal_at: datetime = None


class ResponseUser(BaseDTO):
    id: int = None
    email: str = None
    name: str = None
    last_name: str = None
    patronymic: str = None
    phone: str = None
    inner_phone: int = None
    is_active: bool = True
    photo_path: str = None
    deparment: str = None
    position: str = None

class ResponseList(BaseModel):
    pagination: Pagination
    users: list[UserResponse]