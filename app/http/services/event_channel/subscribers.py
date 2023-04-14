from aioredis.client import PubSub
from json import dumps

__all__ = ["subscriber"]

async def subscriber(pubsub: PubSub, channel: str):
    await pubsub.subscribe(channel)
    listen = pubsub.listen()
    async for result in listen:
        yield dumps(result['data'])

