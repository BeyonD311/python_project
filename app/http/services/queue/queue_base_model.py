from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError
from pydantic import validator
from datetime import time
from typing import Any

__all__ = [
    "BaseInfo", 
    "ConfigCalls", 
    "ScriptIVR", 
    "RequestQueue", 
    "RequestQueueMembers", 
    "ResponseQueue", 
    "ResponseQueueMembers", 
    "GetAllQueue", 
    "Filter",
    "ConstField",
    "HyperScriptParams",
    "DefaultParams",
    "User",
    "OuterLines",
    "IvrParams"
]


class ConstField(BaseModel):
    type: str
    name: str
    description: str
    id: str

class HyperScriptParams(BaseModel):
    uuid_form: str = Field('', alias='uuid')
    name: str
    id: str = None
    class Config:
        allow_population_by_field_name = True

class IvrParams(BaseModel):
    id: str
    name: str

class DefaultParams(BaseModel):
    strategy: list[ConstField] = Field([], alias='queue_operator_select_method')
    hyperscript: list[HyperScriptParams] = []
    ivrs: list[IvrParams] = []
    class Config:
        allow_population_by_field_name = True

class BaseInfo(BaseModel):
    """ Общая информация """
    description: str = Field('Кейс 1. Обзвон клиентов, которые заполнили лид-форму', alias='base_info_name')
    exten: int = Field(980, alias='queue_number')
    queue_code: int = Field(4869)
    strategy: str = Field('ringall', alias='queue_operator_select_method')
    weight: int = Field(49050, alias='queue_weight')
    class Config:
        allow_population_by_field_name = True
    @validator('exten')
    def valid_exten(cls, v:int):
        if (v // 100) < 1 or (v // 1000) > 0:
            raise ValidationError("Номер должен состоять 3 цифр")
        return v

class ConfigCalls(BaseModel):
    """ Настройки звонков """
    timeout: time = Field('00:00:56' , alias='duration_call')
    wrapuptime: time = Field('00:00:56', alias='post_call_processing')
    timeout_talk: time = Field('00:02:56', alias='duration_talks')
    timeout_queue: time = Field('00:00:56', alias='max_queue_time')
    maxlen: int = Field(4, alias='max_waiting_in_line')
    class Config:
        allow_population_by_field_name = True

class ScriptIVR(BaseModel):
    """ Сценарии IVR """
    name: str = Field('Название сценария', alias='script_name')
    hyperscript: str = Field('Lorem ipsum dolor sit amet, consectetur', alias='hyperscript')
    class Config:
        allow_population_by_field_name = True

class RequestQueue(BaseModel):
    """ Параметры для создания очереди """
    name: str = Field('', alias='name_queue_operator')
    type_queue: str = Field('', alias='type')
    queue_enabled: bool = Field(True, alias='active')
    base_info: BaseInfo
    config_call: ConfigCalls
    script_ivr: ScriptIVR
    @validator('name')
    def convert_name(cls, v:str):
        v = v.replace(" ", "_")
        return v.lower()

class ResponseQueue(BaseModel):
    """ Параметры для ответа очереди """
    uuid: str = Field()
    name: str = Field('', alias='name_queue_operator')
    type_queue: str = Field('', alias='type')
    queue_enabled: bool = Field(False, alias='active')
    base_info: BaseInfo
    config_call: ConfigCalls
    script_ivr: ScriptIVR
    class Config:
        allow_population_by_field_name = True

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
    operators: list[int] = Field([1005,1002])
    supervisors: list[int] = Field([1001])
    numbers_lines: list[str]

class Filter(BaseModel):
    field: str
    value: Any

class GetAllQueue(BaseModel):
    page: int
    size: int
    filter: list[Filter] = []
    order_field: str
    order_direction:str
