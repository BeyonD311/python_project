import asyncio
from app.http.services.logger_default import get_logger
from app.database import UserRepository
from app.http.services.helpers import RedisInstance
from app.database.repository import Asterisk
from .queue_base_model import RequestQueue

__all__ = ['QueueService']

log = get_logger("QueueService.log")

class QueueService:
    def __init__(self, user_repository: UserRepository, asterisk: Asterisk, redis: RedisInstance) -> None:
        self._repository: UserRepository = user_repository
        self._asterisk: Asterisk = asterisk
        self._redis: RedisInstance = redis
    
    def add(self, params: RequestQueue):
        self._asterisk.add_queue(params=params)
        self._asterisk.execute()
        return params

    def get_queue_by_name(self, name: str):
        queue = self._asterisk.get_queue_by_name(name)
        return queue