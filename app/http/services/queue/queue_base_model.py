from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from pydantic import ValidationError
from datetime import time
from typing import Any

__all__ = ["BaseInfo", "ConfigCalls", "ScriptIVR", "RequestQueue", "RequestQueueMembers", "ResponseQueue", "ResponseQueueMembers", "GetAllQueue", "Filter"]

class BaseInfo(BaseModel):
    """ Общая информация """
    description: str = Field('Кейс 1. Обзвон клиентов, которые заполнили лид-форму', alias='base_info_name')
    queue_number: int = Field(980)
    queue_code: int = Field(4869)
    strategy: str = Field('Автоматически', alias='queue_operator_select_method')
    weight: int = Field(49050, alias='queue_weight')

class ConfigCalls(BaseModel):
    """ Настройки звонков """
    timeout: time = Field('00:00:56' , alias='continue_one_dialer')
    switch_number: int = Field(506, alias='switch_number')
    timeout_talk: time = Field('"00:02:56', alias='duration_talks')
    timeout_queue: time = Field('00:00:56', alias='duration_call')
    max_len: int = Field(4, alias='simul_incoming_calls')

class ScriptIVR(BaseModel):
    """ Сценарии IVR """
    name: str = Field('Название сценария', alias='script_name')
    greeting: str = Field('Lorem ipsum dolor sit amet, consectetur')
    hyperscript: str = Field('Lorem ipsum dolor sit amet, consectetur', alias='hyperscript')
    post_call: str = Field('Lorem ipsum dolor sit amet, consectetur', alias='post_call_processing')
    service_script: str = Field('Lorem ipsum dolor sit amet, consectetur', alias='service_script')

class RequestQueue(BaseModel):
    """ Параметры для создания очереди """
    name: str = Field('', alias='name_queue_operator')
    type: str = Field('', alias='type')
    active: bool
    base_info: BaseInfo
    config_call: ConfigCalls
    script_ivr: ScriptIVR

class ResponseQueue(BaseModel):
    """ Параметры для создания очереди """
    uuid: str
    name: str = Field('', alias='name_queue_operator')
    type: str = Field('', alias='type')
    active: bool
    base_info: BaseInfo
    config_call: ConfigCalls
    script_ivr: ScriptIVR

class User(BaseModel):
    inner_phone: int
    position: int


class OuterLines(BaseModel):
    name: str
    is_selected: bool = False

class ResponseQueueMembers(BaseModel):
    operators: list[User] = []
    supervisors: list[User] = []
    numbers_lines: list[OuterLines] = []
    

class RequestQueueMembers(BaseModel):
    operators: list[User] = Field([
        User(inner_phone=1005, position=2),
        User(inner_phone=1002, position=2)
    ])
    supervisors: list[User] = Field([
        User(inner_phone=1001, position=1)
    ])
    numbers_lines: list[OuterLines]

class Filter(BaseModel):
    field: str
    value: Any

class GetAllQueue(BaseModel):
    page: int
    size: int
    filter: list[Filter] = []
    order_field: str
    order_direction:str