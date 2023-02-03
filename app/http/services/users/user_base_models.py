from pydantic import BaseModel
from datetime import datetime

class UserLoginParams(BaseModel):
    login: str
    password: str

""" Поля пользователя """
class UserResponse(BaseModel):
    id: int = None
    email: str = None
    password: str = None
    name: str = None
    last_name: str = None
    patronymic: str = None
    login: str = None
    is_operator: bool = None
    phone: str = None
    inner_phone: int = None
    is_active: bool = True
    photo_path: str = None
    date_employment_at: datetime = None
    date_dismissal_at: datetime = None
    created_at: datetime = None
    updated_at: datetime = None

class UserRequest(BaseModel):
    id: int = None
    email: str = None
    password: str = None
    name: str = None
    last_name: str = None
    patronymic: str = None
    login: str = None
    is_operator: bool = None
    phone: str = None
    inner_phone: int = None
    is_active: bool = True
    photo_path: str = None
    date_employment_at: datetime = None
    date_dismissal_at: datetime = None
    created_at: datetime = None
    updated_at: datetime = None

__all__ = ('UserLoginParams', 'UserResponse', 'UserRequest')