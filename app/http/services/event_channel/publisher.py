from json import dumps
from enum import Enum
from pydantic import BaseModel
from aioredis import Redis

__all__ = ["Params", "publisher", "EventRoute"]

class Params(BaseModel):
    user_id: int
    status_id: int
    status_cod: str
    status_at: str
    color: str = None
    incoming_call: str = None
    event: str = None

class EventRoute(Enum):
    CALL = "NEW_CALL"
    BUSY = "CHANGE_STATUS"
    BREAK = "CHANGE_STATUS"
    READY = "CHANGE_STATUS"
    OFFLINE = "CHANGE_STATUS"
    AFTERCALL = "HANGUP_CALL"
    HANGUP = "HANGUP_CALL"
    DISMISS = "CHANGE_STATUS"
    

async def publisher(redis: Redis, channel: str, params: Params):
    await redis.publish(channel, dumps(params))
    
