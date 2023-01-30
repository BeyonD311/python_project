import time, os, base64, jwt
from dotenv import load_dotenv
from fastapi import Depends, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException


class AuthHandler():
    load_dotenv()

    SECRET_KEY = os.getenv('JWT_PRIVATE_KEY')
    ALGORITHM = os.getenv('JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRES_IN = int(os.getenv('ACCESS_TOKEN_EXPIRES_IN')) * 60
    REFRESH_TOKEN_EXPIRES_IN = int(os.getenv('ACCESS_TOKEN_EXPIRES_IN')) * 60 * 60 * 24

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
                                       key=base64.b64decode(self.SECRET_KEY), algorithms=[self.ALGORITHM])
        except jwt.exceptions.InvalidTokenError:
            return ("Invalid token")
        return decoded_token if decoded_token["expire_time"] >= time.time() else False


    def send_cookies(self, access_token, refresh_token, response: Response):
        response.set_cookie('access_token', access_token, self.ACCESS_TOKEN_EXPIRES_IN * 60,
                            self.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
        response.set_cookie('refresh_token', refresh_token, self.REFRESH_TOKEN_EXPIRES_IN * 60 * 60 * 24,
                            self.REFRESH_TOKEN_EXPIRES_IN * 60 * 60 * 24,
                            '/', None, False, True, 'lax')
        response.set_cookie('logged_in', 'True', self.ACCESS_TOKEN_EXPIRES_IN * 60,
                            self.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

    async def refresh_old_token(self, refresh_token):
        decoded_token = auth_handler.decode_token(refresh_token)
        print(decoded_token)
        if decoded_token is not None:
            # Creating new tokens
            access_token = auth_handler.create_token(self, decoded_token["user_id"], "access_token")
            refresh_token = auth_handler.create_token(self, decoded_token["user_id"], "refresh_token")
            # Setting new cookies with tokens
            # auth_handler.send_cookies(access_token, refresh_token, response)
            return {'new_access_token': access_token, 'new_refresh_token': refresh_token}
        else:
            raise HTTPException(status_code=401, detail='Wrong or expired token was used')


auth_handler = AuthHandler()


class Auth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        next = await call_next(request)
        if "/auth/login" == request.get("path"):
            return next
        if next.status_code == 200:
            print(request.cookies)
            access_token = request.cookies.get("access_token")
            if access_token is not None and auth_handler.decode_token(access_token) is not False:
                print("access token:", auth_handler.decode_token(access_token))
            else:
                refresh_token = request.cookies.get("refresh_token")
                if refresh_token is not None:
                    decoded_token = auth_handler.decode_token(refresh_token)
                    if decoded_token is not False:
                        print("refresh token is not expired", decoded_token)
                        # print(decoded_token['user_id'])
                        # access_token = auth_handler.create_token(decoded_token["user_id"], "access_token")
                        # refresh_token = auth_handler.create_token(decoded_token["user_id"], "refresh_token")
                        # # Setting new cookies with tokens
                        # # auth_handler.send_cookies(access_token, refresh_token, response)
                        # return {'new_access_token': access_token, 'new_refresh_token': refresh_token}
                else:
                    print("no cookies was found")
        else:
            print("Request exception error")

        return next







class ProcessTime(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response



