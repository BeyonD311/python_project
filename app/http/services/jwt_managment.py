import jwt
import os
import json
import asyncio
from datetime import datetime
from aioredis import Redis
from app.database.repository.super import UnauthorizedException
from app.database import UserModel
class Jwt:
    def __init__(self, redis: Redis, user: UserModel = None) -> None:
        self.redis = redis
        self.user = user
        self.timestamp = 0
        self.hour = 3600

    async def _refresh_token(self):
        timestamp = round(datetime.now().timestamp())
        refresh_token = jwt.encode(
            payload={
                "azp": self.user.id,
                "iat": timestamp,
                "exp": timestamp + (self.hour * 24),
                "type": "r"
            },
            key=os.getenv("SECRET_KEY"),
            algorithm="HS256"
        )
        return refresh_token

    async def _access_token(self):
        timestamp = round(datetime.now().timestamp())
        self.timestamp = timestamp + (10 * 60)
        access_token = jwt.encode(
            payload={
                "azp": self.user.id,
                "iat": timestamp,
                "exp": timestamp + (10 * 60),
                "type": "a"
            },
            key=os.getenv("SECRET_KEY"),
            algorithm="HS256"
        )
        return access_token

    async def add_to_black_list(self, token: str):
        await self.check_black_list(token)
        await asyncio.sleep(0.5)
        # время жизни неделя
        await self.redis.set(name = f"users:black_list:{token}", value= 0, ex=(self.hour * 24) * 7)

    async def check_black_list(self, token: str):
        black_list = await self.redis.get(f"users:black_list:{token}")
        if black_list is not None:
            raise TokenInBlackList

    async def tokens(self):
        access = await self._access_token()
        refresh = await self._refresh_token()
        tokens = {
            "access_token": access.decode('utf-8'),
            "refresh_token": refresh.decode('utf-8'),
            "life_time": 10 * 60
        }
        await self.redis.set(f"user:token:{self.user.id}", json.dumps(tokens))
        return tokens
    
    async def get_tokens(self):
        tokens = await self.redis.get(f"user:token:{self.user.id}")
        if tokens is None:
            raise TokenNotFound
        return json.loads(tokens)
    
    async def remove_token(self):
        await self.redis.delete(f"user:token:{self.user.id}")

    async def __aenter__(self):
        return self
    async def __aexit__(self, *args):
        print("EXIT async with")

class JwtManagement:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
    
    async def generate(self, user: UserModel = None):
        return Jwt(self.redis, user)
    
class TokenNotFound(UnauthorizedException):
    def __init__(self) -> None:
        message = "Token not found"
        description = "Не найден токен авторизации"
        super().__init__(entity_message=message, entity_description=description)

class TokenInBlackList(UnauthorizedException):
    def __init__(self) -> None:
        message = "Token in black list"
        description = "Токен заблокирован"
        super().__init__(entity_message=message, entity_description=description)

__all__ = ["JwtManagement"]
