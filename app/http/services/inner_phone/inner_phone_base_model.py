from datetime import time
from pydantic import BaseModel

__all__ = ["InnerPhone", "RequestInnerPhone"]

class InnerPhone(BaseModel):
    id: int = None
    phone_number: int
    description: str = None
    registration: bool = False
    default: bool = False
    login: str
    password: str
    duration_call: time = "00:00:00"
    duration_conversation: time = "00:00:00"
    incoming_calls: int = 0
    comment: str = None
    

class RequestInnerPhone(BaseModel):
    user_id: int
    inner_phones: list[InnerPhone]
