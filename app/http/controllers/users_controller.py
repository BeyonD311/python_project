from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, status, Depends, HTTPException
from pydantic import EmailStr
from passlib.context import CryptContext

from app.http.services.users.user_base_models import CreateUserSchema
import app.kernel as kernel
from app.http.services.users import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
route = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not found"}}
)


@route.get("/")
@inject
async def get_users(user_service: UserService = Depends(Provide[kernel.Container.user_service])):
    return user_service.get_users()


@route.post('/register', status_code=status.HTTP_201_CREATED)
@inject
async def create_user(payload: CreateUserSchema,
                      user_service: UserService = Depends(Provide[kernel.Container.user_service])):
    # Validation of login
    if not user_service.validate_new_login(payload.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong login')
    # Validation of email
    if not user_service.validate_new_email(payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Used wrong email')
    # Check if user already exist
    if user_service.check_user(payload.email, payload.name):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Account already exist')
    # Compare password and passwordConfirm
    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
    #  Hash the password
    payload.password = hash_password(payload.password)
    del payload.passwordConfirm
    payload.email = EmailStr(payload.email.lower())

    user_service.create_user(payload.name, payload.email, payload.password)
    return {'data': 'user was created'}


def hash_password(password: str):
    return pwd_context.hash(password)
