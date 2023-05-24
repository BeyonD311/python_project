import aiohttp
from os import getenv
from enum import Enum
from .logger_default import get_logger

logger = get_logger(f"{__name__}.txt")

URI = getenv("SUTECRM_URI")

async def send_contact_post(phone: str, id = None) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URI}/api/call/phone", json={"phone":phone}) as res:
            logger.debug(await res.json())
            return res.status


async def send_call_post(id: str, phone: str) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URI}/call", json={"id":id, "phone":phone}) as res:
            return res.status

async def send_call_patch(id: str, disposition:str, duration: int,  audio_name='', direction:str = "Outbound",):
    async with aiohttp.ClientSession() as session:
        async with session.patch(f"{URI}/call", params={'id':id, 'disposition':disposition, 'duration': duration, 'direction':direction, 'audio_name':audio_name}) as res:
            return res.status


Events = {
    "PRECALL": send_contact_post,
    "CALLWATING": send_contact_post,
    "CALLBACK": send_call_post,
    "EXTERNALCALL": send_call_post
}