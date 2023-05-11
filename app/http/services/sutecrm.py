import aiohttp, json
from os import getenv
from pydantic import BaseModel

HOST = getenv("SUTECRM_HOST")
PORT = getenv("SUTECRM_POST")

async def send_call_post(id: str, phone: str) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{HOST}:{PORT}/api/call", json={"id":id, "phone":phone}) as res:
            return res.status

async def send_call_patch(id: str, disposition:str, duration: int, direction:str = "Outbound"):
    async with aiohttp.ClientSession() as session:
        async with session.patch(f"{HOST}:{PORT}/api/call", json={id:id, disposition:disposition, duration: duration, direction:direction}) as res:
            return res.status