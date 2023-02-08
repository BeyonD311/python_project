import jwt
import os
import json
from datetime import datetime
from fastapi import Request
from aioredis import Redis
from app.database import UserModel
from app.http.services import RolesPermission

class Jwt:
    def __init__(self, redis: Redis, user: UserModel) -> None:
        self.redis = redis
        self.user = user
        self.timestamp = 0
    async def _refresh_token(self):
        timestamp = round(datetime.now().timestamp())
        refresh_token = jwt.encode(
            payload={
                "azp": self.user.id,
                "iat": timestamp,
                "exp": timestamp + 86400
            },
            key=os.getenv("SECRET_KEY"),
            algorithm="HS256"
        )
        return refresh_token
    async def _access_token(self):
        timestamp = round(datetime.now().timestamp())
        self.timestamp = timestamp + (10 * 60)
        roles_result = {}
        for role in self.user.roles:
            roles_result[role.id] = {}
            for access in role.permission_model:
                roles_result[role.id][access.module_id] = access.method_access
        access_token = jwt.encode(
            payload={
                "azp": self.user.id,
                "iat": timestamp,
                "exp": timestamp + (10 * 60),
                "rol": roles_result
            },
            key=os.getenv("SECRET_KEY"),
            algorithm="HS256"
        )
        return access_token
    async def add_to_black_list(self, access_token: str, id:str):
        black_list = await self.redis.get(f"users:black_list:{id}")
        if black_list is not None:
            black_list = json.decoder(json.decoder(black_list))
        else:
            black_list = {}
        if access_token in black_list:
            raise TokenInBlackList
        black_list[access_token] = 0
        await self.redis.set(f"users:black_list:{id}", json.dums(black_list.encode('utf-8')))

    async def tokens(self):
        access = await self._access_token()
        refresh = await self._refresh_token()
        tokens = {
            "access_token": access.decode('utf-8'),
            "refresh_token": refresh.decode('utf-8'),
            "life_time": self.timestamp
        }
        await self.redis.set(f"user.{self.user.id}", json.dumps(tokens))
        return tokens
    
    async def get_tokens(self, id):
        tokens = await self.redis.get(f"users:{id}")
        if tokens is None:
            raise TokenNotFound
        return tokens
    
    async def __aenter__(self):
        return self
    async def __aexit__(self, *args):
        print("EXIT async with")

class JwtManagement:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
    
    async def generate(self, user: UserModel):
        return Jwt(self.redis, user)
    
class TokenNotFound(Exception):
    def __init__(self, id) -> None:
        super().__init__(f"Token not found {id}")

class TokenInBlackList(Exception):
    def __init__(self) -> None:
        super().__init__("Token in black list")

__all__ = ["JwtManagement"]