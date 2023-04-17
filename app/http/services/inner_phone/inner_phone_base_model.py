from datetime import time
from pydantic import BaseModel, Field

__all__ = ["InnerPhone", "RequestInnerPhone", "Settings", "Account", "Design", "Options"]


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


class Design(BaseModel):
    theme: str = 'dark'
    show_dialpad: bool = Field(True, alias='showDialpad')
    show_history: bool = Field(True, alias='showHistory')


class Options(BaseModel):
    display_name: str = Field('', alias='displayName')
    ring_sound: str = Field('ring', alias='ringSound')
    allow_multiple_active_calls: bool = Field(False, alias='allowMultipleActiveCalls')
    incoming_call_limit: int = Field(0, alias='incomingCallLimit')
    auto_answer: bool = Field(False, alias='autoAnswer')
    auto_answer_timeout: int = Field(5, alias='autoAnswerTimeout')
    codecs_audio: str = Field('', alias='codecsAudio')
    codecs_video: str = Field('', alias='codecsVideo')
    codecs_video_disable_rtx: bool = Field(False, alias='codecsVideoDisableRTX')
    log_level: str = Field('error', alias='logLevel')
    default_transfer_phone: bool = Field(True, alias='defaultTransferPhone')


class Account(BaseModel):
    id: str
    name: str
    enabled: bool = True
    engine_type: str = Field('SipJS', alias='engineType')
    user_name: str = Field(alias='userName')
    domain_name: str = Field(alias='domainName')
    login: str
    password: str
    server_address: str = Field(alias='serverAddress')
    server_port: str = Field(alias='serverPort')
    is_register: bool = Field(alias='register')
    video: bool = False


class Settings(BaseModel):
    version: str = '1.0.0'
    accounts: list[Account]
    design: Design
    options: Options
