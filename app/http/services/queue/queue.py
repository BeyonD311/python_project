import datetime, json
from aioredis import Redis
from app.http.services.logger_default import get_logger
from app.database import UserRepository
from app.http.services.helpers import RedisInstance
from app.database.repository.asterisk import Asterisk

log = get_logger("QueueService.log")

class QueueService:
    def __init__(self, user_repository: UserRepository, asterisk: Asterisk, redis: RedisInstance) -> None:
        self._repository: UserRepository = user_repository
        self._asterisk: Asterisk = asterisk
        self._redis: RedisInstance = redis
    
    