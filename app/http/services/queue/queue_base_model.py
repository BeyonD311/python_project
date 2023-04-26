import asyncio
from pydantic import BaseModel
from pydantic import Field
from datetime import time

__all__ = ["BaseInfo", "ConfigCalls", "ScriptIVR", "RequestQueue", "RequestQueueMembers"]

class BaseInfo(BaseModel):
    """ Общая информация """
    name: str = Field('Кейс 1. Обзвон клиентов, которые заполнили лид-форму')
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

class RequestQueueMembers(BaseModel):
    operators: list[int]
    supervisors: list[int]
    numbers_lines: list[int]
