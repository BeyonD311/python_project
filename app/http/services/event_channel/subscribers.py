from aioredis.client import PubSub
from json import dumps

__all__ = ["subscriber"]

async def subscriber(pubsub: PubSub, user_id:int):
    await pubsub.subscribe(f"user:status:{user_id}:c")
    listen = pubsub.listen()
    async for result in listen:
        yield dumps(result['data'])

