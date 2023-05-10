import aiohttp, json
from os import getenv
from pydantic import BaseModel


async def send_call_post(id: str, phone: str):
    host = getenv("SUTECRM_HOST")
    port = getenv("SUTECRM_POST")
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{host}:{port}/api/call", data=json.dumps({id:"1003", phone:"1003"})) as res:
            print(res.status, f"{host}:{port}/api/call")
            r = await res.json()
            print(r)