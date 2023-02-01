from pydantic import BaseModel
from datetime import datetime

class UserLoginParams(BaseModel):
    login: str
    password: str
""" Поля пользователя """
class UserParams(BaseModel):
    id: int
    email: str
    hashed_password: str
    password: str
    name: str
    last_name: str
    patronymic: str
    login: str
    is_operator: bool
    phone: str
    inner_phone: int
    is_active: bool
    photo_path: str
    date_employment_at: datetime
    date_dismissal_at: datetime
    created_at: datetime
    updated_at: datetime