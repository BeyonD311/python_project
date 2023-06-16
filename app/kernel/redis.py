from typing import AsyncIterator
from app.http.services.logger_default import get_logger
from aioredis import from_url, Redis
import json, pprint

log = get_logger("redis_connection.log")

async def init_redis_pool(host: str, password: str, attempts: int = 0 ) -> AsyncIterator[Redis]:
    if attempts < 3:
        try:
            session = from_url(f"redis://{host}/0", password=password, encoding="utf-8", decode_responses=True, health_check_interval=30)
            session.single_connection_client = True
            yield session
            await session.close()
        except ConnectionError as error:
            log.error(error)
            init_redis_pool(host, password, attempts+1)