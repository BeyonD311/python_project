from datetime import timedelta
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import status, HTTPException

from app.http.services.users.user_base_models import LoginUserSchema
from app.http.services.users import UserService
import app.kernel as kernel
import os, base64, time, jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import status, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class AuthHandler():
    load_dotenv()
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    SECRET_KEY = os.getenv('JWT_PRIVATE_KEY')
    ALGORITHM = os.getenv('JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRES_IN = int(os.getenv('ACCESS_TOKEN_EXPIRES_IN')) * 60
    REFRESH_TOKEN_EXPIRES_IN = int(os.getenv('ACCESS_TOKEN_EXPIRES_IN')) * 60 * 60 * 24

    def hash_password(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

# Delete
    def get_user_id(self, login: str, user_service: UserService):
        return user_service.return_user_id(login)

    def authenticate_user(self, login: str, password: str, user_service: UserService):
        exist: bool = False
        if user_service.check_login(login):
            if self.verify_password(password, user_service.get_hashed_password(login)):
                exist = True
        else:
            exist = False
        return exist

    def encode_token(self, user_id: int, token_type: str):
        if token_type == "access_token":
            expire_time = time.time() + self.ACCESS_TOKEN_EXPIRES_IN
        else:
            expire_time = time.time() + self.REFRESH_TOKEN_EXPIRES_IN
        payload: dict = {
            'user_id': user_id,
            'expire_time': expire_time,
            'token_type': token_type
        }
        return jwt.encode(payload, base64.b64decode(self.SECRET_KEY), algorithm=self.ALGORITHM).decode('utf-8').strip()

    def create_token(self, user_id: int, token_type: str):
        new_token = self.encode_token(user_id, token_type)
        return new_token

    def decode_token(self, refresh_token):
        try:
            decoded_token = jwt.decode(refresh_token,
                                       base64.b64decode(self.SECRET_KEY), algorithms=[self.ALGORITHM])
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

        return decoded_token if decoded_token["token_type"] == "refresh_token" \
                                and decoded_token["expire_time"] >= time.time() else False

    def get_current_user(self, access_token: str, user_service: UserService):
        payload = jwt.decode(access_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='User id not found')
        user = user_service.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='User not found')
        return user

    def auth_access_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    def auth_refresh_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    def send_cookies(self, access_token, refresh_token, response: Response):
        response.set_cookie('access_token', access_token, self.ACCESS_TOKEN_EXPIRES_IN * 60,
                            self.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
        response.set_cookie('refresh_token', refresh_token, self.REFRESH_TOKEN_EXPIRES_IN * 60 * 60 * 24,
                            self.REFRESH_TOKEN_EXPIRES_IN * 60 * 60 * 24,
                            '/', None, False, True, 'lax')
        response.set_cookie('logged_in', 'True', self.ACCESS_TOKEN_EXPIRES_IN * 60,
                            self.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

    async def refresh_old_token(self, refresh_token, response: Response):
        decoded_token = handler.decode_token(refresh_token)
        if decoded_token is not False:
            # Creating new tokens
            access_token = handler.create_token(decoded_token["user_id"], "access_token")
            refresh_token = handler.create_token(decoded_token["user_id"], "refresh_token")
            # Setting new cookies with tokens
            handler.send_cookies(access_token, refresh_token, response)
            return {'new_access_token': access_token, 'new_refresh_token': refresh_token}
        else:
            raise HTTPException(status_code=401, detail='Wrong or expired token was used')






route = APIRouter(
    prefix="/auth",
    tags=['auth'],
)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
handler = AuthHandler()


@route.post('/login')
@inject
async def token(response: Response, payload: LoginUserSchema,
                user_service: UserService = Depends(Provide[kernel.Container.user_service])):
    # post_data = await request.post()

    if not handler.authenticate_user(payload.login, payload.password, user_service):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='Wrong login or password')
    user_id = handler.get_user_id(payload.login, user_service)
    # Creating tokens
    access_token = handler.create_token(user_id, "access_token")
    refresh_token = handler.create_token(user_id, "refresh_token")
    # Setting cookies with tokens
    handler.send_cookies(access_token, refresh_token, response)

    return {'atatus': 'success', 'access_token': access_token, 'refresh_token': refresh_token}


@route.post('/refresh')
async def refresh_jwt(refresh_token, response: Response):
    decoded_token = handler.decode_token(refresh_token)
    if decoded_token is not False:
        # Creating new tokens
        access_token = handler.create_token(decoded_token["user_id"], "access_token")
        refresh_token = handler.create_token(decoded_token["user_id"], "refresh_token")
        # Setting new cookies with tokens
        handler.send_cookies(access_token, refresh_token, response)
        return {'new_access_token': access_token, 'new_refresh_token': refresh_token}
    else:
        raise HTTPException(status_code=401, detail='Wrong or expired token was used')


@route.get('/some_action')
def some_action():
    return {'status': 'some_action'}


# Logout using HTTPAuthorizationCredentials and access_token
@route.get('/logout', status_code=status.HTTP_200_OK)
# def logout(response: Response, Authorize: AuthJWT = Depends(), user_id: str = Depends(require_user)):
# def logout(response: Response, login=Depends(handler.auth_access_wrapper)):
def logout(response: Response):
    # Authorize.jwt_required()
    # Authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', expires=0)
    response.set_cookie('access_token', '', expires=0)
    response.set_cookie('refresh_token', '', expires=0)

    return {'status': 'Successfully logout'}


# @route.get("/update_token")
# def update_token(payload=Depends(handler.auth_refresh_wrapper)):
#     if payload is None:
#         raise HTTPException(status_code=401, detail="not authorization")
#     user_id = payload["user_id"]
#     access_token = handler.create_token(user_id, "access_token")
#     refresh_token = handler.create_token(user_id, "refresh_token")
#
#     return {'access_token': access_token, 'refresh_token': refresh_token}
