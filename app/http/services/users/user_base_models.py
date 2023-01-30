import uuid
from pydantic import BaseModel, EmailStr, constr


class UserLoginParams(BaseModel):
    login: str
    password: str


class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserResponse(UserBaseSchema):
    id: uuid.UUID
    # created_at: datetime
    # updated_at: datetime


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=8)
    passwordConfirm: str
    # role: str = 'user'
    # verified: bool = False


class LoginUserSchema(BaseModel):
    login: str
    password: constr(min_length=8)
