from pydantic import BaseModel

class UserLoginParams(BaseModel):
    login: str
    password: str